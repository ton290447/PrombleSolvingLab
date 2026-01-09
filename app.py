import streamlit as st
import uuid
import os

# --- Song Class (Linked List Node) ---
class Song:
    def __init__(self, title, artist, file_bytes=None, mime_type=None, filename=None):
        self.id = str(uuid.uuid4())
        self.title = title
        self.artist = artist
        self.file_bytes = file_bytes
        self.mime_type = mime_type
        self.filename = filename
        self.next_song = None

    def __str__(self):
        return f"{self.title} by {self.artist}"

# --- MusicPlaylist Class (Singly Linked List) ---
class MusicPlaylist:
    def __init__(self):
        self.head = None
        self.current_song = None
        self.length = 0

    def add_song(self, title, artist, file_bytes=None, mime_type=None, filename=None):
        new_song = Song(title, artist, file_bytes, mime_type, filename)

        if self.head is None:
            self.head = new_song
            self.current_song = new_song
        else:
            cur = self.head
            while cur.next_song:
                cur = cur.next_song
            cur.next_song = new_song

        self.length += 1
        st.success(f"Added: {new_song}")

    def to_list(self):
        items = []
        cur = self.head
        idx = 1
        while cur:
            items.append({
                "idx": idx,
                "id": cur.id,
                "title": cur.title,
                "artist": cur.artist,
                "filename": cur.filename,
                "has_audio": cur.file_bytes is not None
            })
            cur = cur.next_song
            idx += 1
        return items

    def set_current_by_id(self, song_id):
        cur = self.head
        while cur:
            if cur.id == song_id:
                self.current_song = cur
                return True
            cur = cur.next_song
        return False

    def play_current_song(self):
        if not self.current_song:
            st.warning("Playlist is empty or no song is selected.")
            return

        st.info(f"Now playing: {self.current_song}")

        if self.current_song.file_bytes:
            fmt = self.current_song.mime_type or guess_mime(self.current_song.filename)
            st.audio(self.current_song.file_bytes, format=fmt)
        else:
            st.warning("This song has no uploaded audio file attached.")

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

        cur = self.head
        while cur.next_song != self.current_song:
            cur = cur.next_song
        self.current_song = cur

    def delete_song_by_id(self, song_id):
        if self.head is None:
            st.error("Cannot delete. Playlist is empty.")
            return

        if self.head.id == song_id:
            if self.current_song == self.head:
                self.current_song = self.head.next_song
            self.head = self.head.next_song
            self.length -= 1
            st.success("Deleted selected song.")
            if self.length == 0:
                self.current_song = None
            return

        prev = self.head
        cur = self.head.next_song

        while cur and cur.id != song_id:
            prev = cur
            cur = cur.next_song

        if not cur:
            st.error("Song not found.")
            return

        if self.current_song == cur:
            self.current_song = cur.next_song if cur.next_song else prev

        prev.next_song = cur.next_song
        self.length -= 1
        st.success("Deleted selected song.")
        if self.length == 0:
            self.current_song = None

    def get_length(self):
        return self.length


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


# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Music Playlist App", page_icon="🎶")
st.title("🎶 Music Playlist App (Upload & Play Real Audio)")

if "playlist" not in st.session_state:
    st.session_state.playlist = MusicPlaylist()

playlist = st.session_state.playlist

st.sidebar.header("⬆️ Upload Song File(s)")
uploaded_files = st.sidebar.file_uploader(
    "Choose audio file(s)",
    type=["mp3", "wav", "ogg", "m4a"],
    accept_multiple_files=True
)
st.sidebar.caption("Tip: MP3/WAV/OGG จะชัวร์สุดเรื่องเล่นได้ในเบราว์เซอร์")

st.sidebar.markdown("---")
st.sidebar.subheader("Optional info (ใช้กับไฟล์เดียวเท่านั้น)")
manual_title = st.sidebar.text_input("Title (optional)")
manual_artist = st.sidebar.text_input("Artist (optional)")

if st.sidebar.button("Add Uploaded Songs to Playlist"):
    if not uploaded_files:
        st.sidebar.warning("Please upload at least 1 audio file.")
    else:
        for f in uploaded_files:
            file_bytes = f.getvalue()
            mime_type = f.type
            filename = f.name

            base_title = os.path.splitext(filename)[0]

            if len(uploaded_files) > 1:
                title = base_title
                artist = "Unknown Artist"
            else:
                title = manual_title.strip() if manual_title.strip() else base_title
                artist = manual_artist.strip() if manual_artist.strip() else "Unknown Artist"

            playlist.add_song(title, artist, file_bytes=file_bytes, mime_type=mime_type, filename=filename)

st.header("📃 Your Current Playlist")

items = playlist.to_list()
if not items:
    st.write("Playlist is empty. Upload songs from the sidebar!")
else:
    options = {
        f'{it["idx"]}. {it["title"]} — {it["artist"]} {"✅" if it["has_audio"] else "❌"}': it["id"]
        for it in items
    }

    current_id = playlist.current_song.id if playlist.current_song else None
    default_label = None
    for label, sid in options.items():
        if sid == current_id:
            default_label = label
            break

    selected_label = st.selectbox(
        "Select a song (✅ = has audio file)",
        list(options.keys()),
        index=list(options.keys()).index(default_label) if default_label else 0
    )
    selected_id = options[selected_label]

    if st.button("Set as Current Song"):
        playlist.set_current_by_id(selected_id)
        st.success("Current song updated!")

    st.markdown("---")
    st.subheader("🎧 Current Song Player")
    playlist.play_current_song()

    st.markdown("---")
    st.subheader("🕹️ Playback Controls")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⏪ Previous"):
            playlist.prev_song()
            playlist.play_current_song()

    with col2:
        if st.button("▶️ Play Current"):
            playlist.play_current_song()

    with col3:
        if st.button("⏩ Next"):
            playlist.next_song()
            playlist.play_current_song()

    st.markdown("---")
    st.subheader("🗑️ Delete Song")
    if st.button("Delete Selected Song"):
        playlist.delete_song_by_id(selected_id)

st.markdown("--- 🎶")
st.write(f"Total songs in playlist: {playlist.get_length()} song(s)")
