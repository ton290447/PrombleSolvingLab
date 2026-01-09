import streamlit as st
import os

# --- Song Class ---
class Song:
    def __init__(self, title, artist, audio_bytes=None, audio_type=None, filename=None):
        self.title = title
        self.artist = artist
        self.audio_bytes = audio_bytes   # เก็บไฟล์เพลง (bytes)
        self.audio_type = audio_type     # mime type เช่น audio/mpeg, audio/wav
        self.filename = filename         # ชื่อไฟล์
        self.next_song = None

    def __str__(self):
        return f"{self.title} by {self.artist}"

# --- MusicPlaylist Class ---
class MusicPlaylist:
    def __init__(self):
        self.head = None
        self.current_song = None
        self.length = 0

    def add_song(self, title, artist, audio_bytes=None, audio_type=None, filename=None):
        new_song = Song(title, artist, audio_bytes, audio_type, filename)

        if self.head is None:
            self.head = new_song
            self.current_song = new_song
        else:
            current = self.head
            while current.next_song:
                current = current.next_song
            current.next_song = new_song

        self.length += 1
        st.success(f"Added: {new_song}")

    def display_playlist(self):
        if self.head is None:
            return []

        playlist_songs = []
        current = self.head
        count = 1
        while current:
            mark = "🎵" if current.audio_bytes else "📝"
            playing = "  ▶️ (Current)" if current == self.current_song else ""
            playlist_songs.append(f"{count}. {mark} {current.title} by {current.artist}{playing}")
            current = current.next_song
            count += 1
        return playlist_songs

    def play_current_song(self):
        if not self.current_song:
            st.warning("Playlist is empty or no song is selected to play.")
            return

        st.info(f"Now playing: {self.current_song}")

        # ถ้ามีไฟล์เพลงจริง -> แสดงตัวเล่นเพลง
        if self.current_song.audio_bytes:
            fmt = self.current_song.audio_type or guess_mime(self.current_song.filename)
            st.audio(self.current_song.audio_bytes, format=fmt)
        else:
            st.warning("เพลงนี้ยังไม่มีไฟล์เสียงแนบมา (เพิ่มเพลงแบบอัปโหลดไฟล์)")

    def next_song(self):
        if self.current_song and self.current_song.next_song:
            self.current_song = self.current_song.next_song
        elif self.current_song and not self.current_song.next_song:
            st.warning("End of playlist. No next song.")
        else:
            st.warning("Playlist is empty.")

    def prev_song(self):
        if self.head is None or self.current_song is None:
            st.warning("Playlist is empty or no song is selected.")
            return
        if self.current_song == self.head:
            st.warning("Already at the beginning of the playlist.")
            return

        current = self.head
        while current.next_song != self.current_song:
            current = current.next_song
        self.current_song = current

    def get_length(self):
        return self.length

    def delete_song(self, title):
        if self.head is None:
            st.error(f"Cannot delete '{title}'. Playlist is empty.")
            return

        if self.head.title == title:
            if self.current_song == self.head:
                self.current_song = self.head.next_song
            self.head = self.head.next_song
            self.length -= 1
            st.success(f"Deleted: {title}")
            if self.length == 0:
                self.current_song = None
            return

        current = self.head
        prev = None
        while current and current.title != title:
            prev = current
            current = current.next_song

        if current:
            if self.current_song == current:
                self.current_song = current.next_song if current.next_song else prev

            prev.next_song = current.next_song
            self.length -= 1
            st.success(f"Deleted: {title}")
        else:
            st.error(f"Song '{title}' not found in the playlist.")

def guess_mime(filename):
    if not filename:
        return "audio/mpeg"
    ext = os.path.splitext(filename.lower())[1]
    if ext == ".mp3":
        return "audio/mpeg"
    if ext == ".wav":
        return "audio/wav"
    if ext == ".ogg":
        return "audio/ogg"
    if ext == ".m4a":
        return "audio/mp4"
    return "audio/mpeg"


# --- Streamlit App Layout ---
st.title("🎶 Music Playlist App")

# Initialize playlist in session state
if 'playlist' not in st.session_state:
    st.session_state.playlist = MusicPlaylist()

# Sidebar for adding songs
st.sidebar.header("Add New Song")
new_title = st.sidebar.text_input("Title")
new_artist = st.sidebar.text_input("Artist")

# ✅ เพิ่มอัปโหลดไฟล์เพลง
uploaded_audio = st.sidebar.file_uploader(
    "Upload Audio File (Optional)",
    type=["mp3", "wav", "ogg", "m4a"]
)

if st.sidebar.button("Add Song to Playlist"):
    if new_title and new_artist:
        audio_bytes = None
        audio_type = None
        filename = None

        if uploaded_audio is not None:
            audio_bytes = uploaded_audio.getvalue()
            audio_type = uploaded_audio.type
            filename = uploaded_audio.name

        st.session_state.playlist.add_song(
            new_title, new_artist,
            audio_bytes=audio_bytes, audio_type=audio_type, filename=filename
        )
    else:
        st.sidebar.warning("Please enter both title and artist.")

st.sidebar.markdown("--- 🎶")
st.sidebar.header("Delete Song")
delete_title = st.sidebar.text_input("Song Title to Delete")
if st.sidebar.button("Delete Song"):
    if delete_title:
        st.session_state.playlist.delete_song(delete_title)
    else:
        st.sidebar.warning("Please enter a song title to delete.")

# Main content for playlist display and controls
st.header("Your Current Playlist")
playlist_content = st.session_state.playlist.display_playlist()
if playlist_content:
    for song_str in playlist_content:
        st.write(song_str)
else:
    st.write("Playlist is empty. Add some songs from the sidebar!")

st.markdown("--- 🎶")
st.header("Playback Controls")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⏪ Previous"):
        st.session_state.playlist.prev_song()

with col2:
    if st.button("▶️ Play Current"):
        st.session_state.playlist.play_current_song()

with col3:
    if st.button("⏩ Next"):
        st.session_state.playlist.next_song()

# ✅ แสดงตัวเล่นเพลงไว้ข้างล่างด้วย (เห็นชัด)
st.markdown("--- 🎧")
st.subheader("Now Playing Player")
st.session_state.playlist.play_current_song()

st.markdown("--- 🎶")
st.write(f"Total songs in playlist: {st.session_state.playlist.get_length()} song(s)")
