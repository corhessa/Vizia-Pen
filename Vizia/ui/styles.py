# ui/styles.py

TOOLTIP_STYLE = """
    QToolTip {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #d1d1d6;
        border-radius: 4px;
        padding: 5px;
        font-family: 'Segoe UI';
        font-size: 12px;
        font-weight: bold;
    }
"""

TOOLBAR_STYLESHEET = f"""
    QWidget {{ 
        background-color: #1c1c1e; 
        border-radius: 20px; 
        border: 1.5px solid #3a3a3c; 
    }}
    
    QPushButton {{ 
        background-color: #2c2c2e; 
        color: white; 
        border: none; 
        border-radius: 10px; 
        padding: 6px;
    }}
    
    QPushButton:hover {{ 
        background-color: #3a3a40; 
        border: 1px solid #007aff; 
    }}

    QPushButton[active="true"] {{
        background-color: #007aff;
        border: 1px solid white;
    }}
    
    QPushButton[state="red"] {{ background-color: #ff3b30; }}
    QPushButton[state="green"] {{ background-color: #4cd964; }}
    
    QPushButton#btn_shot {{
        background-color: #5856d6;
    }}
    
    QLabel {{ 
        color: white; 
        background: transparent; 
        border: none; 
    }}
    
    /* --- SLIDER STİLİ (GERİ EKLENDİ) --- */
    QSlider {{ margin-top: -4px; background: transparent; }}
    
    QSlider::groove:horizontal {{ 
        background: #3a3a3c; 
        height: 4px; 
        border-radius: 2px; 
    }}
    
    QSlider::sub-page:horizontal {{
        background: #007aff; 
        border-radius: 2px;
    }}
    
    QSlider::handle:horizontal {{ 
        background: #ffffff; 
        border: 2px solid #007aff; 
        width: 14px; 
        height: 14px; 
        margin: -5px 0; 
        border-radius: 7px; 
    }}
    
    QSlider::handle:horizontal:hover {{
        background: #f0f0f0; 
        border: 2px solid #005bb5;
    }}
    
    {TOOLTIP_STYLE}
"""

def get_color_btn_style(color_hex):
    return f"""
        QPushButton {{ color: {color_hex}; font-size: 20px; font-weight: bold; }}
        {TOOLTIP_STYLE}
    """

