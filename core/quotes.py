"""
Motivational quotes module for Focus Timer.
Shows random quotes during breaks to inspire users.
"""

import random
from typing import List, Tuple

# Collection of motivational quotes (quote, author)
MOTIVATIONAL_QUOTES: List[Tuple[str, str]] = [
    ("The secret of getting ahead is getting started.", "Mark Twain"),
    ("It's not that I'm so smart, it's just that I stay with problems longer.", "Albert Einstein"),
    ("Focus on being productive instead of busy.", "Tim Ferriss"),
    ("The way to get started is to quit talking and begin doing.", "Walt Disney"),
    ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
    ("Concentrate all your thoughts upon the work at hand.", "Alexander Graham Bell"),
    ("The successful warrior is the average man, with laser-like focus.", "Bruce Lee"),
    ("Lack of direction, not lack of time, is the problem.", "Zig Ziglar"),
    ("Action is the foundational key to all success.", "Pablo Picasso"),
    ("You don't have to be great to start, but you have to start to be great.", "Zig Ziglar"),
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
    ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
    ("Your time is limited, don't waste it living someone else's life.", "Steve Jobs"),
    ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
    ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
    ("Quality is not an act, it is a habit.", "Aristotle"),
    ("The mind is everything. What you think you become.", "Buddha"),
    ("Strive not to be a success, but rather to be of value.", "Albert Einstein"),
    ("In the middle of difficulty lies opportunity.", "Albert Einstein"),
    ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
    ("Your limitation—it's only your imagination.", "Unknown"),
    ("Push yourself, because no one else is going to do it for you.", "Unknown"),
    ("Great things never come from comfort zones.", "Unknown"),
    ("Dream it. Wish it. Do it.", "Unknown"),
    ("Success doesn't just find you. You have to go out and get it.", "Unknown"),
    ("The harder you work for something, the greater you'll feel when you achieve it.", "Unknown"),
    ("Dream bigger. Do bigger.", "Unknown"),
    ("Don't stop when you're tired. Stop when you're done.", "Unknown"),
    ("Wake up with determination. Go to bed with satisfaction.", "Unknown"),
    ("Do something today that your future self will thank you for.", "Sean Patrick Flanery"),
    ("Little things make big days.", "Unknown"),
    ("It's going to be hard, but hard does not mean impossible.", "Unknown"),
    ("Don't wait for opportunity. Create it.", "Unknown"),
    ("Sometimes we're tested not to show our weaknesses, but to discover our strengths.", "Unknown"),
    ("The key is not to prioritize what's on your schedule, but to schedule your priorities.", "Stephen Covey"),
    ("One day or day one. You decide.", "Unknown"),
    ("Stay focused, go after your dreams and keep moving toward your goals.", "LL Cool J"),
    ("Focus is a matter of deciding what things you're not going to do.", "John Carmack"),
    ("Productivity is never an accident.", "Paul J. Meyer"),
]

# Break-specific quotes (for showing during break time)
BREAK_QUOTES: List[Tuple[str, str]] = [
    ("Rest when you're weary. Refresh and renew yourself.", "Ralph Marston"),
    ("Almost everything will work again if you unplug it for a few minutes, including you.", "Anne Lamott"),
    ("Take rest; a field that has rested gives a bountiful crop.", "Ovid"),
    ("Your calm mind is the ultimate weapon against your challenges.", "Bryant McGill"),
    ("The time to relax is when you don't have time for it.", "Sydney J. Harris"),
    ("Breathe. Let go. And remind yourself that this very moment is the only one you know you have for sure.", "Oprah Winfrey"),
    ("Sometimes the most productive thing you can do is relax.", "Mark Black"),
    ("Tension is who you think you should be. Relaxation is who you are.", "Chinese Proverb"),
    ("Give your stress wings and let it fly away.", "Terri Guillemets"),
    ("Rest is not idleness.", "John Lubbock"),
]


class QuoteManager:
    """Manages motivational quotes for the app."""
    
    def __init__(self):
        self._last_quote_index = -1
        self._last_break_quote_index = -1
    
    def get_random_quote(self) -> Tuple[str, str]:
        """Get a random motivational quote. Returns (quote, author)."""
        index = random.randint(0, len(MOTIVATIONAL_QUOTES) - 1)
        # Avoid repeating the same quote
        while index == self._last_quote_index and len(MOTIVATIONAL_QUOTES) > 1:
            index = random.randint(0, len(MOTIVATIONAL_QUOTES) - 1)
        self._last_quote_index = index
        return MOTIVATIONAL_QUOTES[index]
    
    def get_break_quote(self) -> Tuple[str, str]:
        """Get a random break-time quote. Returns (quote, author)."""
        index = random.randint(0, len(BREAK_QUOTES) - 1)
        # Avoid repeating the same quote
        while index == self._last_break_quote_index and len(BREAK_QUOTES) > 1:
            index = random.randint(0, len(BREAK_QUOTES) - 1)
        self._last_break_quote_index = index
        return BREAK_QUOTES[index]
    
    def get_all_quotes(self) -> List[Tuple[str, str]]:
        """Get all motivational quotes."""
        return MOTIVATIONAL_QUOTES.copy()
    
    def get_all_break_quotes(self) -> List[Tuple[str, str]]:
        """Get all break quotes."""
        return BREAK_QUOTES.copy()


# Global instance
quote_manager = QuoteManager()


def get_random_quote() -> Tuple[str, str]:
    """Convenience function to get a random quote."""
    return quote_manager.get_random_quote()


def get_break_quote() -> Tuple[str, str]:
    """Convenience function to get a break quote."""
    return quote_manager.get_break_quote()
