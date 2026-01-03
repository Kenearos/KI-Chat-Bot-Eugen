"""
Tests for ConversationMemory class
"""
import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta
from memory import ConversationMemory


class TestConversationMemory:
    """Test ConversationMemory functionality"""

    def test_init_creates_data_directory(self, temp_dir):
        """Test that data directory is created on init"""
        data_dir = temp_dir / "conversations"
        memory = ConversationMemory(data_dir=str(data_dir))
        assert data_dir.exists()

    def test_get_user_file_sanitizes_username(self, temp_dir):
        """Test that usernames are sanitized for filesystem"""
        memory = ConversationMemory(data_dir=str(temp_dir))
        # Special characters should be removed
        file_path = memory._get_user_file("User@#$Name!")
        assert "@" not in file_path.name
        assert "#" not in file_path.name
        assert "!" not in file_path.name
        assert "username" in file_path.name.lower()

    def test_get_user_file_lowercase(self, temp_dir):
        """Test that user file names are lowercase"""
        memory = ConversationMemory(data_dir=str(temp_dir))
        file_path = memory._get_user_file("TestUser")
        assert file_path.name == "testuser.json"

    def test_add_message_creates_file(self, temp_dir):
        """Test that adding message creates user file"""
        memory = ConversationMemory(data_dir=str(temp_dir))
        memory.add_message("testuser", "user", "Hello!")

        user_file = temp_dir / "testuser.json"
        assert user_file.exists()

    def test_add_message_stores_content(self, temp_dir):
        """Test that message content is stored correctly"""
        memory = ConversationMemory(data_dir=str(temp_dir))
        memory.add_message("testuser", "user", "Hello bot!")

        user_file = temp_dir / "testuser.json"
        with open(user_file, 'r') as f:
            history = json.load(f)

        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello bot!"
        assert "timestamp" in history[0]

    def test_add_message_appends_to_existing(self, temp_dir):
        """Test that messages are appended to existing history"""
        memory = ConversationMemory(data_dir=str(temp_dir))
        memory.add_message("testuser", "user", "First message")
        memory.add_message("testuser", "assistant", "Response")
        memory.add_message("testuser", "user", "Second message")

        user_file = temp_dir / "testuser.json"
        with open(user_file, 'r') as f:
            history = json.load(f)

        assert len(history) == 3
        assert history[0]["content"] == "First message"
        assert history[1]["content"] == "Response"
        assert history[2]["content"] == "Second message"

    def test_add_message_enforces_max_limit(self, temp_dir):
        """Test that max message limit is enforced"""
        memory = ConversationMemory(data_dir=str(temp_dir), max_messages=5)

        # Add 10 messages
        for i in range(10):
            memory.add_message("testuser", "user", f"Message {i}")

        user_file = temp_dir / "testuser.json"
        with open(user_file, 'r') as f:
            history = json.load(f)

        # Should only keep last 5
        assert len(history) == 5
        assert history[0]["content"] == "Message 5"
        assert history[4]["content"] == "Message 9"

    def test_get_user_history_empty_for_new_user(self, temp_dir):
        """Test that new users have empty history"""
        memory = ConversationMemory(data_dir=str(temp_dir))
        history = memory.get_user_history("newuser")
        assert history == []

    def test_get_user_history_returns_messages(self, temp_dir):
        """Test that user history is retrieved correctly"""
        memory = ConversationMemory(data_dir=str(temp_dir))
        memory.add_message("testuser", "user", "Message 1")
        memory.add_message("testuser", "assistant", "Response 1")

        history = memory.get_user_history("testuser")
        assert len(history) == 2
        assert history[0]["content"] == "Message 1"
        assert history[1]["content"] == "Response 1"

    def test_get_user_history_respects_limit(self, temp_dir):
        """Test that limit parameter works"""
        memory = ConversationMemory(data_dir=str(temp_dir))

        # Add 10 messages
        for i in range(10):
            memory.add_message("testuser", "user", f"Message {i}")

        # Request only 3
        history = memory.get_user_history("testuser", limit=3)
        assert len(history) == 3
        # Should get the most recent 3
        assert history[0]["content"] == "Message 7"
        assert history[2]["content"] == "Message 9"

    def test_get_user_history_filters_by_retention_time(self, temp_dir):
        """Test that old messages are filtered out"""
        memory = ConversationMemory(data_dir=str(temp_dir), retention_hours=1)

        # Manually create history with old and new messages
        now = datetime.now()
        old_time = now - timedelta(hours=2)
        recent_time = now - timedelta(minutes=10)

        history_data = [
            {
                "role": "user",
                "content": "Old message",
                "timestamp": old_time.isoformat()
            },
            {
                "role": "user",
                "content": "Recent message",
                "timestamp": recent_time.isoformat()
            }
        ]

        user_file = temp_dir / "testuser.json"
        with open(user_file, 'w') as f:
            json.dump(history_data, f)

        # Get history - should only return recent
        retrieved = memory.get_user_history("testuser")
        assert len(retrieved) == 1
        assert retrieved[0]["content"] == "Recent message"

    def test_get_user_history_handles_corrupted_json(self, temp_dir):
        """Test that corrupted JSON is handled gracefully"""
        memory = ConversationMemory(data_dir=str(temp_dir))

        # Create corrupted JSON file
        user_file = temp_dir / "testuser.json"
        user_file.write_text("{ invalid json")

        # Should return empty history and not crash
        history = memory.get_user_history("testuser")
        assert history == []

    def test_get_user_history_handles_invalid_timestamps(self, temp_dir):
        """Test that messages with invalid timestamps are skipped"""
        memory = ConversationMemory(data_dir=str(temp_dir))

        history_data = [
            {
                "role": "user",
                "content": "Message with bad timestamp",
                "timestamp": "not-a-timestamp"
            },
            {
                "role": "user",
                "content": "Valid message",
                "timestamp": datetime.now().isoformat()
            }
        ]

        user_file = temp_dir / "testuser.json"
        with open(user_file, 'w') as f:
            json.dump(history_data, f)

        retrieved = memory.get_user_history("testuser")
        # Should skip invalid and return valid
        assert len(retrieved) == 1
        assert retrieved[0]["content"] == "Valid message"

    def test_format_for_prompt(self, temp_dir, sample_conversation_history):
        """Test formatting history for API prompt"""
        memory = ConversationMemory(data_dir=str(temp_dir))

        formatted = memory.format_for_prompt(sample_conversation_history)

        assert len(formatted) == 4
        # Should only have role and content, no timestamp
        assert "role" in formatted[0]
        assert "content" in formatted[0]
        assert "timestamp" not in formatted[0]

        assert formatted[0]["role"] == "user"
        assert formatted[0]["content"] == "Hello bot!"
        assert formatted[1]["role"] == "assistant"

    def test_clear_user_history_removes_file(self, temp_dir):
        """Test that clearing history removes the user file"""
        memory = ConversationMemory(data_dir=str(temp_dir))
        memory.add_message("testuser", "user", "Hello!")

        user_file = temp_dir / "testuser.json"
        assert user_file.exists()

        memory.clear_user_history("testuser")
        assert not user_file.exists()

    def test_clear_user_history_nonexistent_user(self, temp_dir):
        """Test clearing history for user that doesn't exist"""
        memory = ConversationMemory(data_dir=str(temp_dir))
        # Should not crash
        memory.clear_user_history("nonexistent")

    def test_get_all_users(self, temp_dir):
        """Test getting list of all users with history"""
        memory = ConversationMemory(data_dir=str(temp_dir))
        memory.add_message("user1", "user", "Hello")
        memory.add_message("user2", "user", "Hi")
        memory.add_message("user3", "user", "Hey")

        users = memory.get_all_users()
        assert len(users) == 3
        assert "user1" in users
        assert "user2" in users
        assert "user3" in users

    def test_get_all_users_empty(self, temp_dir):
        """Test getting all users when no history exists"""
        memory = ConversationMemory(data_dir=str(temp_dir))
        users = memory.get_all_users()
        assert users == []

    def test_get_user_message_count(self, temp_dir):
        """Test getting message count for a user"""
        memory = ConversationMemory(data_dir=str(temp_dir))
        memory.add_message("testuser", "user", "Message 1")
        memory.add_message("testuser", "assistant", "Response 1")
        memory.add_message("testuser", "user", "Message 2")

        count = memory.get_user_message_count("testuser")
        assert count == 3

    def test_get_user_message_count_new_user(self, temp_dir):
        """Test message count for new user"""
        memory = ConversationMemory(data_dir=str(temp_dir))
        count = memory.get_user_message_count("newuser")
        assert count == 0

    def test_get_user_message_count_corrupted_file(self, temp_dir):
        """Test message count with corrupted file"""
        memory = ConversationMemory(data_dir=str(temp_dir))

        user_file = temp_dir / "testuser.json"
        user_file.write_text("{ corrupted")

        count = memory.get_user_message_count("testuser")
        assert count == 0

    def test_unicode_content_support(self, temp_dir):
        """Test that German/Unicode characters are supported"""
        memory = ConversationMemory(data_dir=str(temp_dir))
        memory.add_message("testuser", "user", "Äpfel und Öle über ß")

        history = memory.get_user_history("testuser")
        assert history[0]["content"] == "Äpfel und Öle über ß"

    def test_special_characters_in_username(self, temp_dir):
        """Test usernames with special characters"""
        memory = ConversationMemory(data_dir=str(temp_dir))
        # Twitch usernames can have underscores
        memory.add_message("user_name_123", "user", "Hello")

        history = memory.get_user_history("user_name_123")
        assert len(history) == 1

    def test_concurrent_access_simulation(self, temp_dir):
        """Test that multiple adds don't corrupt data"""
        memory = ConversationMemory(data_dir=str(temp_dir))

        # Simulate rapid message additions
        for i in range(20):
            memory.add_message("testuser", "user", f"Message {i}")

        history = memory.get_user_history("testuser", limit=20)
        assert len(history) == 20
        # Verify all messages are present and in order
        for i, msg in enumerate(history):
            assert msg["content"] == f"Message {i}"

    def test_retention_hours_edge_case(self, temp_dir):
        """Test retention exactly at the boundary"""
        memory = ConversationMemory(data_dir=str(temp_dir), retention_hours=1)

        now = datetime.now()
        exactly_one_hour = now - timedelta(hours=1, seconds=1)
        just_under_one_hour = now - timedelta(minutes=59)

        history_data = [
            {
                "role": "user",
                "content": "Exactly at boundary",
                "timestamp": exactly_one_hour.isoformat()
            },
            {
                "role": "user",
                "content": "Just under boundary",
                "timestamp": just_under_one_hour.isoformat()
            }
        ]

        user_file = temp_dir / "testuser.json"
        with open(user_file, 'w') as f:
            json.dump(history_data, f)

        retrieved = memory.get_user_history("testuser")
        # Only message within retention should be kept
        assert len(retrieved) == 1
        assert retrieved[0]["content"] == "Just under boundary"

    def test_add_message_handles_read_error_gracefully(self, temp_dir, mocker):
        """Test that add_message handles file read errors gracefully"""
        memory = ConversationMemory(data_dir=str(temp_dir))

        # Create a file first
        memory.add_message("testuser", "user", "First message")

        # Mock json.load to raise an exception
        mocker.patch("json.load", side_effect=PermissionError("Permission denied"))

        # Should not crash, should handle the error gracefully
        memory.add_message("testuser", "user", "Second message")

    def test_add_message_handles_write_error_gracefully(self, temp_dir, mocker):
        """Test that add_message handles file write errors gracefully"""
        memory = ConversationMemory(data_dir=str(temp_dir))

        # Mock json.dump to raise an exception
        mocker.patch("json.dump", side_effect=IOError("Disk full"))

        # Should not crash even when write fails
        memory.add_message("testuser", "user", "Test message")

    def test_clear_user_history_handles_permission_error(self, temp_dir, mocker):
        """Test that clear_user_history handles permission errors gracefully"""
        memory = ConversationMemory(data_dir=str(temp_dir))

        # Create a user file
        memory.add_message("testuser", "user", "Test message")

        # Mock unlink to raise permission error
        mocker.patch("pathlib.Path.unlink", side_effect=PermissionError("Permission denied"))

        # Should not crash
        memory.clear_user_history("testuser")
