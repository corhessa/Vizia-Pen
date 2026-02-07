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

# Toolbar'ın ana stili (Tooltip stilini de içine dahil ediyoruz)
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
        font-size: 18px; 
        min-width: 40px; 
        min-height: 40px; 
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
    
    /* KAMERA BUTONU ÖZEL RENGİ */
    QPushButton#btn_shot {{
        background-color: #5856d6;
    }}
    QPushButton#btn_shot:hover {{
        border: 1px solid white;
    }}
    
    QLabel {{ 
        color: white; 
        background: transparent; 
        border: none; 
    }}
    
    {TOOLTIP_STYLE}
"""

# Renk butonu için dinamik stil oluşturucu
def get_color_btn_style(color_hex):
    return f"""
        QPushButton {{ color: {color_hex}; font-size: 20px; }}
        {TOOLTIP_STYLE}
    """