import streamlit as st
import time
import os
import sys
import re
import requests
import base64
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apertus.apertus import LangchainApertus

st.set_page_config(
    layout="wide",
    page_title="Tomorrow's Legal Assistance",
    page_icon="frontend/media/favicon.ico"
)

# Custom CSS for styling
st.markdown("""
<style>
.stApp {
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

def format_chat_history_for_markdown(messages):
    markdown_string = ""
    for message in messages:
        role = "User" if message["role"] == "user" else "Assistant"
        markdown_string += f"**{role}:**\n"
        markdown_string += message["content"] + "\n\n"
        markdown_string += "---\n\n"
    return markdown_string

def sanitize_filename(filename):
    return re.sub(r'[^\w\s-]', '', filename).strip()

# Sidebar for chat management
with st.sidebar:
    st.image("frontend/media/AXA_Versicherungen_Logo.svg.png", width=150)
    
    # Audio control
    st.markdown("### 🎵 Background Music")
    
    # Initialize audio state
    if "audio_enabled" not in st.session_state:
        st.session_state.audio_enabled = False
    
    # Initialize audio ID for unique element identification
    if "audio_id" not in st.session_state:
        st.session_state.audio_id = hash(str(time.time()))
    
    # Audio toggle button
    audio_button_text = "🔊 Music ON" if st.session_state.audio_enabled else "🔇 Music OFF"
    if st.button(audio_button_text, key="audio_toggle"):
        st.session_state.audio_enabled = not st.session_state.audio_enabled
        st.rerun()
    
    # Show audio status and player when enabled
    if st.session_state.audio_enabled:
        st.success("🎶 Music will play during analysis")
        
        # Load audio file
        audio_file_path = "frontend/media/apertus.mp3"
        with open(audio_file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        # Show visible audio player for user control and testing
        st.write("**Audio Player (for testing and manual control):**")
        st.audio(audio_bytes, format='audio/mp3')
        
        # Instructions for the user
        st.info("""
        **How to enable background music:**
        1. Click play on the audio player above once (this enables audio permissions)
        2. You can then pause it - the background music will work during analysis
        3. If music doesn't auto-play during analysis, try clicking anywhere on the page first
        """)
        
        # Create JavaScript-controlled audio player
        audio_b64 = base64.b64encode(audio_bytes).decode()
        
        # Embed hidden background audio player
        st.markdown(f"""
        <audio id="background-audio-player" loop preload="auto" style="display: none;">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        
        <script>
        (function() {{
            // Initialize background audio
            window.backgroundAudio = document.getElementById('background-audio-player');
            
            if (window.backgroundAudio) {{
                window.backgroundAudio.volume = 0.2; // Lower volume for background
                console.log('Background audio initialized');
                
                // Enable audio context after user interaction
                let audioEnabled = false;
                
                function enableAudioContext() {{
                    if (!audioEnabled && window.backgroundAudio) {{
                        // Create a minimal audio context to enable autoplay
                        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                        if (audioContext.state === 'suspended') {{
                            audioContext.resume();
                        }}
                        audioEnabled = true;
                        console.log('Audio context enabled');
                    }}
                }}
                
                // Listen for any user interaction to enable audio
                ['click', 'touchstart', 'keydown'].forEach(event => {{
                    document.addEventListener(event, enableAudioContext, {{ once: true }});
                }});
                
                window.startBackgroundMusic = function() {{
                    if (window.backgroundAudio) {{
                        console.log('Attempting to start background music...');
                        enableAudioContext(); // Ensure audio is enabled
                        
                        window.backgroundAudio.currentTime = 0;
                        window.backgroundAudio.play()
                            .then(() => {{
                                console.log('Background music started successfully');
                            }})
                            .catch(e => {{
                                console.log('Background music play failed:', e);
                                console.log('Try clicking anywhere on the page first to enable audio');
                            }});
                    }}
                }};
                
                window.stopBackgroundMusic = function() {{
                    if (window.backgroundAudio && !window.backgroundAudio.paused) {{
                        console.log('Stopping background music...');
                        window.backgroundAudio.pause();
                        window.backgroundAudio.currentTime = 0;
                    }}
                }};
                
                // Test function
                window.testBackgroundMusic = function() {{
                    console.log('Testing background music for 5 seconds...');
                    window.startBackgroundMusic();
                    setTimeout(() => {{
                        window.stopBackgroundMusic();
                        console.log('Background music test completed');
                    }}, 5000);
                }};
            }} else {{
                console.log('Background audio element not found');
            }}
        }})();
        </script>
        """, unsafe_allow_html=True)
        
        # Add test button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎵 Test Background Music (5sec)", key="test_bg_music"):
                st.markdown("""
                <script>
                if (window.testBackgroundMusic) {
                    window.testBackgroundMusic();
                } else {
                    console.log('Test function not available');
                }
                </script>
                """, unsafe_allow_html=True)
                st.success("Testing background music for 5 seconds...")
        
        with col2:
            if st.button("🔇 Stop Music", key="stop_music"):
                st.markdown("""
                <script>
                if (window.stopBackgroundMusic) {
                    window.stopBackgroundMusic();
                }
                </script>
                """, unsafe_allow_html=True)
                st.info("Stopped background music")
    else:
        st.info("🔇 Music is disabled")
    
    st.markdown("---")
    
    if st.button("New Chat"):
        st.session_state.clear()
        st.rerun()

    if st.session_state.get("messages"):
        if st.button("Delete Chat"):
            st.session_state.clear()
            st.rerun()

        chat_history_md = format_chat_history_for_markdown(st.session_state.messages)
        
        file_name = "chat_history.md"
        if "chat_title" in st.session_state:
            sanitized_title = sanitize_filename(st.session_state.chat_title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{sanitized_title}_{timestamp}.md"
        
        st.download_button(
            label="Save Chat",
            data=chat_history_md,
            file_name=file_name,
            mime="text/markdown",
        )
        
        # Add PDF downloads if source documents are available in the most recent assistant message
        if "source_documents" in st.session_state:
            st.subheader("📄 Source Documents")
            for doc in st.session_state.source_documents:
                doc_id = doc.get('id', '')
                title = doc.get('title', 'Unknown Document')
                
                # Handle fallback documents differently
                if 'fallback' in doc_id:
                    st.info(f"📚 **{title}**\n\nThis is reference information about Swiss employment law. The actual Code of Obligations (SR-220) PDF is available but not currently indexed in the search system.")
                    
                    # Try to find the actual SR-220 PDF
                    sr220_files = [f for f in os.listdir(os.path.join(os.path.dirname(__file__), "..", "data", "swiss_law")) 
                                  if f.startswith("SR-220")]
                    if sr220_files:
                        pdf_path = os.path.join(os.path.dirname(__file__), "..", "data", "swiss_law", sr220_files[0])
                        with open(pdf_path, "rb") as pdf_file:
                            pdf_data = pdf_file.read()
                        
                        st.download_button(
                            label=f"📖 Download {sr220_files[0]} (Code of Obligations)",
                            data=pdf_data,
                            file_name=sr220_files[0],
                            mime="application/pdf",
                            key=f"download_{sr220_files[0]}"
                        )
                else:
                    # Regular document - try to find PDF
                    filename = title if title.endswith('.pdf') else f"{title}.pdf"
                    pdf_path = os.path.join(os.path.dirname(__file__), "..", "data", "swiss_law", filename)
                    
                    if os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as pdf_file:
                            pdf_data = pdf_file.read()
                        
                        st.download_button(
                            label=f"📖 {filename}",
                            data=pdf_data,
                            file_name=filename,
                            mime="application/pdf",
                            key=f"download_{filename}"
                        )
                    else:
                        st.warning(f"PDF not found: {filename}")

st.title("Tomorrow's Legal Assistant")

if "chat_title" in st.session_state:
    st.subheader(st.session_state.chat_title)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display initial message if chat is empty
if not st.session_state.messages:
    st.info("Welcome! Please describe your legal situation in the chat below.")

# Display chat messages from history
for message in st.session_state.messages:
    avatar_path = "frontend/media/Gemini_Generated_Image_wl26p8wl26p8wl26_zoomin.png" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar_path):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is your legal question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Main logic for processing user input
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    prompt = st.session_state.messages[-1]["content"]

    # Step 1: Generate Title (if not exists) and rerun
    if "chat_title" not in st.session_state:
        api_key = os.environ.get("APERTUS_API_KEY")
        if api_key:
            # Start background music if enabled
            if st.session_state.get("audio_enabled", False):
                st.markdown("""
                <script>
                setTimeout(function() {
                    console.log('Starting music for title generation...');
                    if (window.startBackgroundMusic) {
                        window.startBackgroundMusic();
                    } else {
                        console.log('startBackgroundMusic function not available');
                    }
                }, 100);
                </script>
                """, unsafe_allow_html=True)
            
            with st.spinner("Generating title..."):
                try:
                    llm = LangchainApertus(api_key=api_key)
                    title_prompt = f"""You are an expert title generator. Your mission is to create a concise, filename-safe title from a user's query.

                    ### Your Instructions
                    1.  **Word Count:** The title MUST be 5 words or less.
                    2.  **Content:** Your response MUST contain ONLY the words of the title.
                    3.  **Formatting:** The title MUST be plain text, free of quotation marks or any prefixes like "Title:".
                    4.  **No Commentary:** You MUST NOT add any notes or explanations. Your entire response is the title.
                    5.  **Punctuation:** The title MUST end with a word, not with any punctuation like a question mark or period.

                    ### Example
                    Query: "I received a speeding ticket for 500 CHF, can I fight it?"
                    Title: Contesting a 500 CHF Speeding Ticket

                    ### Task
                    Query: '{prompt}'
                    Title:"""
                    response = llm.invoke(title_prompt)
                    clean_title = response.content.strip().split('\n')[0]

                    st.session_state.chat_title = clean_title
                    
                    # Stop background music
                    if st.session_state.get("audio_enabled", False):
                        st.markdown("""
                        <script>
                        if (window.stopBackgroundMusic) {
                            window.stopBackgroundMusic();
                        }
                        </script>
                        """, unsafe_allow_html=True)
                    
                    st.rerun() # Rerun to display title and move to analysis step
                except Exception as e:
                    # Stop background music on error
                    if st.session_state.get("audio_enabled", False):
                        st.markdown("""
                        <script>
                        if (window.stopBackgroundMusic) {
                            window.stopBackgroundMusic();
                        }
                        </script>
                        """, unsafe_allow_html=True)
                    st.error(f"Could not generate title: {e}")
        else:
            st.warning("APERTUS_API_KEY not set. Cannot generate title.")
    
    # Step 2: Generate and display assistant response
    with st.chat_message("assistant", avatar="frontend/media/Gemini_Generated_Image_wl26p8wl26p8wl26_zoomin.png"):
        message_placeholder = st.empty()
        full_response = ""
        
        api_key = os.environ.get("APERTUS_API_KEY")
        if not api_key:
            st.warning("APERTUS_API_KEY not set. Cannot get analysis.")
            st.stop()

        # Start background music if enabled
        if st.session_state.get("audio_enabled", False):
            st.markdown("""
            <script>
            setTimeout(function() {
                console.log('Attempting to start background music...');
                if (window.startBackgroundMusic) {
                    window.startBackgroundMusic();
                } else {
                    console.log('startBackgroundMusic function not available');
                }
            }, 100);
            </script>
            """, unsafe_allow_html=True)

        with st.spinner("Analyzing your situation..."):
            try:
                # Prepare the input for the backend agent
                case_input = {
                    "text": prompt,
                    "metadata": {
                        "language": "en",
                        "court_level": "cantonal",
                        "preferred_units": "months"
                    }
                }

                # Make a POST request to the backend endpoint
                response = requests.post("http://localhost:8000/api/agent_with_tools", json=case_input)
                response.raise_for_status()  # Raise an exception for bad status codes

                # The response from the agent is a JSON object.
                # We need to format it nicely for display.
                analysis_result = response.json()

                # Handle the cost field, which could be a dictionary, string, or number
                cost = analysis_result.get('estimated_cost', 'N/A')
                if isinstance(cost, dict):
                    total_cost = cost.get('total_chf', 'N/A')
                    cost_str = f"{total_cost:.2f} CHF" if isinstance(total_cost, (int, float)) else str(total_cost)
                elif isinstance(cost, str):
                    cost_str = cost  # Already formatted as string like "2500 CHF"
                elif isinstance(cost, (int, float)):
                    cost_str = f"{cost} CHF"
                else:
                    cost_str = 'N/A'

                # Get explanation if available
                explanation = analysis_result.get('explanation', '')
                
                # Format the response into a markdown string
                processed_text = f"""
**Case Category:** {analysis_result.get('category', 'N/A')}

**Likelihood of Winning:** {analysis_result.get('likelihood_win', 'N/A')}

**Estimated Cost:** {cost_str}

**Estimated Timeframe:** {analysis_result.get('estimated_time', 'N/A')}
"""

                # Add explanation if available
                if explanation and explanation.strip():
                    processed_text += f"""
**Detailed Analysis:**

{explanation}
"""

                # Add source documents if available
                source_documents = analysis_result.get('source_documents', [])
                if source_documents:
                    processed_text += """

**Source Documents:**
"""
                    for doc in source_documents:
                        doc_id = doc.get('id', '')
                        title = doc.get('title', 'Unknown Document')
                        snippet = doc.get('snippet', 'No preview available')
                        
                        # Handle fallback documents differently
                        if 'fallback' in doc_id:
                            processed_text += f"""
📄 **{title}**
   - Swiss Employment Law Summary: "{snippet[:300]}..."
   - 📖 Code of Obligations PDF available for download (see sidebar)
"""
                        else:
                            # Regular document
                            filename = title
                            pdf_path = os.path.join(os.path.dirname(__file__), "..", "data", "swiss_law", filename)
                            
                            # Check if file exists and add preview
                            if os.path.exists(pdf_path):
                                processed_text += f"""
📄 **{filename}**
   - Extract: "{snippet[:200]}..."
   - PDF available for download (use sidebar after analysis)
"""
                            else:
                                processed_text += f"""
📄 **{filename}**
   - Extract: "{snippet[:200]}..."
   - (PDF file not accessible)
"""

            except requests.exceptions.RequestException as e:
                # Stop background music on error
                if st.session_state.get("audio_enabled", False):
                    st.markdown("""
                    <script>
                    if (window.stopBackgroundMusic) {
                        window.stopBackgroundMusic();
                    }
                    </script>
                    """, unsafe_allow_html=True)
                st.error(f"Failed to connect to the backend: {e}")
                st.stop()
            except Exception as e:
                # Stop background music on error
                if st.session_state.get("audio_enabled", False):
                    st.markdown("""
                    <script>
                    if (window.stopBackgroundMusic) {
                        window.stopBackgroundMusic();
                    }
                    </script>
                    """, unsafe_allow_html=True)
                st.error(f"An unexpected error occurred: {e}")
                st.stop()

        # Stop background music after successful analysis
        if st.session_state.get("audio_enabled", False):
            st.markdown("""
            <script>
            if (window.stopBackgroundMusic) {
                window.stopBackgroundMusic();
            }
            </script>
            """, unsafe_allow_html=True)

        # Use the processed_text for streaming
        lines = processed_text.split('\n')
        for line in lines:
            full_response += line + "\n"
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        
        # Store source documents in session state for sidebar access
        if source_documents:
            st.session_state.source_documents = source_documents
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()
    
