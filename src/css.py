# Custom CSS for fullscreen image with overlay and styled form components
custom_css = """
/* -------- FULLSCREEN BACKGROUND & NARRATIVE -------- */
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

.overlay-content {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    background: linear-gradient(
        transparent, rgba(0,0,0,0.8)
    ) !important;
    padding: 40px 20px 20px !important;
    z-index: 10 !important;
    color: white !important;
}
.overlay-content .form {
    background: transparent !important;
}

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
.narrative-text textarea {
    background: transparent !important;
    border: none !important;
    color: white !important;
    -webkit-text-fill-color: white !important;
    font-size: 15px !important;
    resize: none !important;
}
img {
    pointer-events: none;
}

/* -------- CHOICE SECTION -------- */
.choice-area {
    background: rgba(0,0,0,0.7) !important;
    border-radius: 10px !important;
    padding: 10px !important;
}

.choice-buttons {
    background: transparent !important;
    border-radius: 10px !important;
    padding: 10px !important;
}
.choice-buttons > div,
.choice-buttons fieldset {
    background: transparent !important;
    border: none !important;
}
.choice-buttons label,
.choice-buttons label span {
    color: white !important;
    font-size: 14px !important;
}
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
.choice-buttons * {
    background-color: transparent !important;
}
.choice-buttons input {
    background-color: transparent !important;
    border: 1px solid rgba(255,255,255,0.5) !important;
    color: white !important;
}

/* Bold legend/label, no background */
.choice-area .form-label,
.choice-area legend {
    background: transparent !important;
    color: white !important;
    border: none !important;
}

/* -------- CUSTOM INPUT FIELD -------- */
.choice-input textarea {
    background: transparent !important;
    border: none !important;
    color: white !important;
    border-radius: 10px !important;
    outline: none !important;
    box-shadow: none !important;
    font-size: 15px !important;
    padding: 10px !important;
}
.choice-input {
    background: none !important;
    margin-top: 10px !important;
}

/* -------- UI MISCELLANEOUS -------- */
.gradio-header,
.gradio-footer {
    display: none !important;
}
.image-container .icon-button-wrapper,
.image-container .icon-buttons {
    display: none !important;
}
#back-btn {
    position: fixed !important;
    top: 10px !important;
    right: 10px !important;
    z-index: 20 !important;
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
    background-color: rgba(0, 0, 0, 0.8);
    justify-content: center;
    align-items: center;
    z-index: 9999;
}
#loading-indicator .loading-text {
    color: white;
    font-size: 2em;
    text-align: center;
}
"""
