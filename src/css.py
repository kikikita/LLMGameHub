# Custom CSS for fullscreen image with overlay
custom_css = """
/* Make the image container fullscreen */
.image-container {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    z-index: 1 !important;
}

.image-container img {
    width: 100vw !important;
    height: 100vh !important;
    object-fit: cover !important;
}

/* Style the overlay content */
.overlay-content {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    background: linear-gradient(transparent, rgba(0,0,0,0.8)) !important;
    padding: 40px 20px 20px !important;
    z-index: 10 !important;
    color: white !important;
}

/* Style the narrative text */
.narrative-text {
    background: rgba(0,0,0,0.7) !important;
    border: none !important;
    color: white !important;
    font-size: 15px !important;
    line-height: 1.5 !important;
    padding: 10px !important;
    border-radius: 10px !important;
    margin-bottom: 10px !important;
}

img {
    pointer-events: none;
}

.narrative-text textarea {
    background: transparent !important;
    border: none !important;
    color: white !important;
    -webkit-text-fill-color: white !important;
    font-size: 15px !important;
    resize: none !important;
}

/* Style the choice buttons */
.choice-buttons {
    background: rgba(0,0,0,0.7) !important;
    border-radius: 10px !important;
    padding: 10px !important;
}

.choice-buttons label {
    color: white !important;
    font-size: 14px !important;
}

/* Fix radio button backgrounds */
.choice-buttons input[type="radio"] {
    background: transparent !important;
    border: 2px solid white !important;
}

.choice-buttons input[type="radio"]:checked {
    background: white !important;
}

.choice-buttons .form-radio {
    background: transparent !important;
}

/* Style radio button containers */
.choice-buttons > div {
    background: transparent !important;
}

.choice-buttons fieldset {
    background: transparent !important;
    border: none !important;
}

/* Remove any remaining white backgrounds */
.choice-buttons * {
    background-color: transparent !important;
}

.choice-buttons input {
    background-color: transparent !important;
    border: 1px solid rgba(255,255,255,0.5) !important;
    color: white !important;
}

/* Style the custom choice textbox */
.custom-choice textarea {
    background: rgba(0,0,0,0.7) !important;
    border: 1px solid rgba(255,255,255,0.5) !important;
    color: white !important;
    border-radius: 10px !important;
}
.custom-choice {
    margin-top: 10px !important;
}

.choice-buttons label span {
    color: white !important;
}

/* Hide gradio header and footer */
.gradio-header, .gradio-footer {
    display: none !important;
}

/* Hide image control buttons using correct DOM selector */
.image-container .icon-button-wrapper {
    display: none !important;
}

.image-container .icon-buttons {
    display: none !important;
}

/* Position the back button in the top-right corner */
#back-btn {
    position: fixed !important;
    top: 10px !important;
    right: 10px !important;
    z-index: 20 !important;
}

/* Make form element transparent */
.overlay-content .form {
    background: transparent !important;
}
"""

# CSS for the loading indicator
loading_css_styles = """
#loading-indicator {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.8); /* Semi-transparent black */
    /* When Gradio makes this gr.Column visible, it will set display:flex !important; (or similar). */
    /* These properties will then apply to center the content of the Column: */
    justify-content: center;
    align-items: center;
    z-index: 9999; /* Ensure it's on top */
}
#loading-indicator .loading-text { /* Style for the text inside */
    color: white;
    font-size: 2em;
    text-align: center;
}
"""
