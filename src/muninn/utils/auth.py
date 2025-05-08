"""
Authentication utilities for Muninn
"""

import os
import logging
from functools import wraps
from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

# Get authorized users from environment variable
AUTHORIZED_USERS = os.getenv("AUTHORIZED_USERS", "")
AUTHORIZED_USERS = [int(user_id.strip()) for user_id in AUTHORIZED_USERS.split(",") if user_id.strip()]

def user_authorized(user_id):
    """Check if the user is authorized to use the bot."""
    return len(AUTHORIZED_USERS) == 0 or user_id in AUTHORIZED_USERS

def restricted(func):
    """Decorator for restricting bot usage to authorized users."""
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if not user_authorized(user_id):
            logger.warning(f"Unauthorized access denied for {user_id}")
            update.message.reply_text("You are not authorized to use this bot.")
            return
        return func(update, context, *args, **kwargs)
    return wrapped 