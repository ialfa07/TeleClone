"""
Clonage de Chaînes Telegram - Fonctionnalité de clonage principale
Gère le clonage réel des messages entre les chaînes Telegram.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from telethon import TelegramClient, errors
from telethon.tl.types import Message

from config import Config
from utils import sanitize_filename, format_duration, calculate_eta


class TelegramCloner:
    """Main class for cloning Telegram channels."""
    
    def __init__(self, config: Config, logger):
        """
        Initialize the Telegram cloner.
        
        Args:
            config: Configuration object
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.client: Optional[TelegramClient] = None
        self.bot_client: Optional[TelegramClient] = None
        
        # Progress tracking
        self.progress_data: Dict[str, Any] = {}
        self.messages_processed = 0
        self.messages_sent = 0
        self.messages_failed = 0
        
    async def clone_channel(
        self,
        source_channel: str,
        target_channel: str,
        message_limit: Optional[int] = None,
        resume: bool = False,
        dry_run: bool = False
    ) -> bool:
        """
        Clone messages from source channel to target channel.
        
        Args:
            source_channel: Source channel username
            target_channel: Target channel username
            message_limit: Maximum number of messages to clone
            resume: Whether to resume from last position
            dry_run: Whether to perform a dry run without sending messages
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Initialisation du client Telegram
            if not self.config.api_id or not self.config.api_hash:
                self.logger.error("Les identifiants API sont requis. Veuillez vérifier votre fichier .env.")
                return False
                
            self.client = TelegramClient(
                self.config.session_name,
                self.config.api_id,
                self.config.api_hash
            )
            
            await self.client.start()
            self.logger.info("Connecté à Telegram avec votre compte")
            
            # Initialiser le client bot si configuré
            if self.config.use_bot_for_sending:
                self.bot_client = TelegramClient(
                    f"{self.config.session_name}_bot",
                    self.config.api_id,
                    self.config.api_hash
                )
                await self.bot_client.start(bot_token=self.config.bot_token)
                self.logger.info("Bot connecté pour l'envoi des messages")
            
            # Obtenir les entités source et cible
            source_entity = await self._get_entity(source_channel)
            if not source_entity:
                return False
                
            target_entity = await self._get_entity(target_channel)
            if not target_entity:
                return False
            
            # Obtenir les titres des entités de manière sécurisée
            source_title = getattr(source_entity, 'title', getattr(source_entity, 'username', str(source_entity.id)))
            target_title = getattr(target_entity, 'title', getattr(target_entity, 'username', str(target_entity.id)))
            
            self.logger.info(f"Source: {source_title}")
            self.logger.info(f"Cible: {target_title}")
            
            # Charger la progression si reprise
            if resume:
                self._load_progress(source_channel, target_channel)
            
            # Obtenir les messages à cloner
            messages = await self._get_messages(source_entity, message_limit)
            if not messages:
                self.logger.warning("Aucun message trouvé à cloner")
                return True
            
            total_messages = len(messages)
            self.logger.info(f"Trouvé {total_messages} messages à cloner")
            
            if dry_run:
                self.logger.info("MODE TEST - Aucun message ne sera envoyé")
                await self._dry_run_analysis(messages)
                return True
            
            # Cloner les messages par lots
            start_time = datetime.now()
            success = await self._clone_messages_batch(
                messages, target_entity, total_messages, start_time
            )
            
            # Sauvegarder la progression finale
            self._save_progress(source_channel, target_channel, completed=success)
            
            # Afficher le résumé
            self._print_summary(start_time)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erreur pendant le clonage: {str(e)}", exc_info=True)
            return False
        finally:
            if self.client:
                await self.client.disconnect()
                self.logger.info("Déconnecté de Telegram")
            if self.bot_client:
                await self.bot_client.disconnect()
                self.logger.info("Bot déconnecté")
    
    async def _get_entity(self, channel_identifier: str):
        """Get Telegram entity for channel."""
        try:
            if not self.client:
                self.logger.error("Telegram client not initialized")
                return None
                
            # Clean channel identifier
            channel_id = channel_identifier.strip()
            if not channel_id.startswith('@') and not channel_id.startswith('+'):
                channel_id = f"@{channel_id}"
            
            entity = await self.client.get_entity(channel_id)
            return entity
        except errors.UsernameNotOccupiedError:
            self.logger.error(f"Channel not found: {channel_identifier}")
        except errors.UsernameInvalidError:
            self.logger.error(f"Invalid channel username: {channel_identifier}")
        except Exception as e:
            self.logger.error(f"Error getting entity for {channel_identifier}: {str(e)}")
        return None
    
    async def _get_messages(self, source_entity, message_limit: Optional[int]) -> List[Message]:
        """Get messages from source channel."""
        try:
            if not self.client:
                self.logger.error("Telegram client not initialized")
                return []
                
            messages = []
            last_message_id = self.progress_data.get('last_message_id', 0)
            
            self.logger.info("Fetching messages from source channel...")
            
            async for message in self.client.iter_messages(
                source_entity,
                reverse=True,
                min_id=last_message_id,
                limit=message_limit or None
            ):
                if message.id <= last_message_id:
                    continue
                messages.append(message)
            
            return messages
        except Exception as e:
            self.logger.error(f"Error fetching messages: {str(e)}")
            return []
    
    async def _clone_messages_batch(
        self,
        messages: List[Message],
        target_entity,
        total_messages: int,
        start_time: datetime
    ) -> bool:
        """Clone messages in batches with rate limiting."""
        batch_messages = []
        
        for i, message in enumerate(messages, 1):
            batch_messages.append(message)
            
            # Process batch when full or at end
            if len(batch_messages) >= self.config.batch_size or i == total_messages:
                success = await self._process_message_batch(
                    batch_messages, target_entity, i, total_messages, start_time
                )
                
                if not success:
                    return False
                
                batch_messages = []
                
                # Rate limiting delay between batches
                if i < total_messages and self.config.rate_limit_delay > 0:
                    await asyncio.sleep(self.config.rate_limit_delay)
        
        return True
    
    async def _process_message_batch(
        self,
        messages: List[Message],
        target_entity,
        current_index: int,
        total_messages: int,
        start_time: datetime
    ) -> bool:
        """Process a batch of messages."""
        for message in messages:
            success = await self._clone_single_message(message, target_entity)
            
            self.messages_processed += 1
            if success:
                self.messages_sent += 1
            else:
                self.messages_failed += 1
            
            # Update progress
            if self.messages_processed % self.config.save_progress_interval == 0:
                self._save_progress_data(message.id)
            
            # Log progress
            if self.messages_processed % 10 == 0:
                self._log_progress(current_index, total_messages, start_time)
        
        return True
    
    async def _clone_single_message(self, message: Message, target_entity) -> bool:
        """Clone a single message with retry logic."""
        for attempt in range(self.config.max_retries + 1):
            try:
                await self._send_message(message, target_entity)
                return True
            except errors.FloodWaitError as e:
                wait_time = e.seconds
                self.logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed for message {message.id}: {str(e)}")
                if attempt < self.config.max_retries:
                    await asyncio.sleep(self.config.retry_delay)
                else:
                    self.logger.error(f"Failed to send message {message.id} after {self.config.max_retries + 1} attempts")
                    return False
        
        return False
    
    async def _send_message(self, message: Message, target_entity):
        """Envoie un message unique vers le canal cible."""
        # Choisir le client approprié pour l'envoi
        send_client = self.bot_client if self.config.use_bot_for_sending else self.client
        
        if not send_client:
            raise Exception("Client d'envoi non initialisé")
            
        # Obtenir le texte du message de manière sécurisée
        message_text = getattr(message, 'message', '') or getattr(message, 'text', '')
        
        try:
            if message_text and not message.media:
                # Message texte uniquement
                await send_client.send_message(target_entity, message_text)
                self.logger.debug(f"Message texte envoyé via {'bot' if self.config.use_bot_for_sending else 'compte utilisateur'}")
                
            elif message.media:
                # Message avec média
                if self.config.download_media:
                    try:
                        await send_client.send_file(
                            target_entity,
                            message.media,
                            caption=message_text or "",
                            parse_mode='html'
                        )
                        self.logger.debug(f"Message média envoyé via {'bot' if self.config.use_bot_for_sending else 'compte utilisateur'}")
                        
                    except Exception as e:
                        self.logger.warning(f"Échec envoi média pour message {message.id}: {str(e)}")
                        # Fallback vers texte uniquement si média échoue
                        if message_text:
                            await send_client.send_message(target_entity, message_text)
                            self.logger.debug("Fallback: texte envoyé sans média")
                else:
                    # Envoyer uniquement le texte si téléchargement média désactivé
                    if message_text:
                        await send_client.send_message(target_entity, message_text)
                        self.logger.debug("Texte envoyé (média ignoré)")
            else:
                # Ignorer les messages vides
                self.logger.debug(f"Message vide {message.id} ignoré")
                
        except Exception as e:
            # Si le bot échoue, essayer avec le compte utilisateur en fallback
            if self.config.use_bot_for_sending and self.client:
                self.logger.warning(f"Bot échoué, tentative avec compte utilisateur: {str(e)}")
                await self._send_message_with_user_client(message, target_entity, message_text)
            else:
                raise e
    
    async def _send_message_with_user_client(self, message: Message, target_entity, message_text: str):
        """Méthode de fallback pour envoyer avec le compte utilisateur."""
        try:
            if message_text and not message.media:
                await self.client.send_message(target_entity, message_text)
            elif message.media and self.config.download_media:
                await self.client.send_file(
                    target_entity,
                    message.media,
                    caption=message_text or "",
                    parse_mode='html'
                )
            elif message_text:
                await self.client.send_message(target_entity, message_text)
            self.logger.debug("Message envoyé avec succès via compte utilisateur (fallback)")
        except Exception as e:
            self.logger.error(f"Échec fallback compte utilisateur: {str(e)}")
            raise e
    
    async def _dry_run_analysis(self, messages: List[Message]):
        """Analyze messages for dry run."""
        text_count = 0
        media_count = 0
        empty_count = 0
        
        for message in messages:
            message_text = getattr(message, 'message', '') or getattr(message, 'text', '')
            if message_text and not message.media:
                text_count += 1
            elif message.media:
                media_count += 1
            else:
                empty_count += 1
        
        self.logger.info(f"Dry run analysis:")
        self.logger.info(f"  Text messages: {text_count}")
        self.logger.info(f"  Media messages: {media_count}")
        self.logger.info(f"  Empty messages: {empty_count}")
        self.logger.info(f"  Total messages: {len(messages)}")
    
    def _load_progress(self, source_channel: str, target_channel: str):
        """Load progress from file."""
        if os.path.exists(self.config.progress_file):
            try:
                with open(self.config.progress_file, 'r') as f:
                    data = json.load(f)
                
                key = f"{source_channel}_{target_channel}"
                if key in data:
                    self.progress_data = data[key]
                    self.logger.info(f"Resuming from message ID: {self.progress_data.get('last_message_id', 0)}")
            except Exception as e:
                self.logger.warning(f"Could not load progress: {str(e)}")
    
    def _save_progress(self, source_channel: str, target_channel: str, completed: bool = False):
        """Save progress to file."""
        try:
            data = {}
            if os.path.exists(self.config.progress_file):
                with open(self.config.progress_file, 'r') as f:
                    data = json.load(f)
            
            key = f"{source_channel}_{target_channel}"
            data[key] = {
                **self.progress_data,
                'completed': completed,
                'last_update': datetime.now().isoformat(),
                'messages_processed': self.messages_processed,
                'messages_sent': self.messages_sent,
                'messages_failed': self.messages_failed
            }
            
            with open(self.config.progress_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save progress: {str(e)}")
    
    def _save_progress_data(self, last_message_id: int):
        """Update progress data."""
        self.progress_data['last_message_id'] = last_message_id
    
    def _log_progress(self, current: int, total: int, start_time: datetime):
        """Log current progress."""
        percentage = (current / total) * 100
        elapsed = datetime.now() - start_time
        eta = calculate_eta(current, total, elapsed)
        
        self.logger.info(
            f"Progress: {current}/{total} ({percentage:.1f}%) - "
            f"Sent: {self.messages_sent}, Failed: {self.messages_failed} - "
            f"ETA: {eta}"
        )
    
    def _print_summary(self, start_time: datetime):
        """Print cloning summary."""
        duration = datetime.now() - start_time
        self.logger.info("=== Cloning Summary ===")
        self.logger.info(f"Total Duration: {format_duration(duration)}")
        self.logger.info(f"Messages Processed: {self.messages_processed}")
        self.logger.info(f"Messages Sent: {self.messages_sent}")
        self.logger.info(f"Messages Failed: {self.messages_failed}")
        
        if self.messages_processed > 0:
            success_rate = (self.messages_sent / self.messages_processed) * 100
            self.logger.info(f"Success Rate: {success_rate:.1f}%")
            
            if duration.total_seconds() > 0:
                rate = self.messages_processed / duration.total_seconds()
                self.logger.info(f"Processing Rate: {rate:.2f} messages/second")
