import os
import re
from typing import Optional

import frontmatter
import markdown
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

# Callout type styling configurations
CALLOUT_STYLES = {
    "info": {"icon": "ℹ️", "bg": "#eff6ff", "border": "#3b82f6", "title_color": "#1e40af"},
    "success": {"icon": "✅", "bg": "#f0fdf4", "border": "#22c55e", "title_color": "#166534"},
    "warning": {"icon": "⚠️", "bg": "#fffbeb", "border": "#f59e0b", "title_color": "#92400e"},
    "danger": {"icon": "🚨", "bg": "#fef2f2", "border": "#ef4444", "title_color": "#991b1b"},
    "tip": {"icon": "💡", "bg": "#fefce8", "border": "#eab308", "title_color": "#854d0e"},
    "note": {"icon": "📝", "bg": "#f5f3ff", "border": "#8b5cf6", "title_color": "#5b21b6"},
    "quote": {"icon": "💬", "bg": "#f9fafb", "border": "#6b7280", "title_color": "#374151"},
    "example": {"icon": "📋", "bg": "#ecfeff", "border": "#06b6d4", "title_color": "#0e7490"},
}


STAT_MAPPINGS = {
    'habit_completion': ('Habits', '✅', '%'),
    'p1_completion': ('P1 Tasks', '🎯', '%'),
    'p2_completion': ('P2 Tasks', '📋', '%'),
    'p3_completion': ('P3 Tasks', '📝', '%'),
    'admin_completion': ('Admin', '⚙️', '%'),
    'avg_energy': ('Energy', '⚡', '/5'),
    'avg_mood': ('Mood', '😊', '/5'),
}


def build_stats_card(metadata: dict) -> str:
    """Build HTML stats card from frontmatter metadata."""
    stats_items = []

    for key, (label, icon, suffix) in STAT_MAPPINGS.items():
        if key in metadata:
            value = metadata[key]
            stats_items.append(f'''
                <div style="text-align: center; padding: 12px;">
                    <div style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">{icon} {label}</div>
                    <div style="font-size: 20px; font-weight: 700; color: #1f2937;">{value}{suffix}</div>
                </div>
            ''')

    if not stats_items:
        return ""

    return f'''
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 12px; padding: 20px; margin-bottom: 24px; border: 1px solid #e2e8f0;">
        <div style="display: flex; flex-wrap: wrap; justify-content: space-around; gap: 8px;">
            {''.join(stats_items)}
        </div>
    </div>
    '''


def convert_obsidian_callouts(content: str) -> str:
    """
    Convert Obsidian-style callouts to HTML divs.

    Obsidian format:
    > [!type] Optional Title
    > content line 1
    > content line 2
    """
    # Pattern to match callout blocks
    callout_pattern = re.compile(
        r'^(?:>\s*\[!(\w+)\]\s*(.*))\n((?:>\s?.*\n?)*)',
        re.MULTILINE
    )

    def replace_callout(match):
        callout_type = match.group(1).lower()
        title = match.group(2).strip()
        content_lines = match.group(3)

        # Get styling for this callout type (default to info)
        style = CALLOUT_STYLES.get(callout_type, CALLOUT_STYLES["info"])

        # Process content lines - remove the > prefix
        lines = []
        for line in content_lines.split('\n'):
            # Remove leading > and optional space
            cleaned = re.sub(r'^>\s?', '', line)
            lines.append(cleaned)

        inner_content = '\n'.join(lines).strip()

        # Convert inner markdown (for bold, lists, etc.)
        md = markdown.Markdown()
        inner_html = md.convert(inner_content)

        # Build the callout HTML
        title_text = title if title else callout_type.capitalize()

        return f'''<div class="callout callout-{callout_type}" style="background: {style['bg']}; border-left: 4px solid {style['border']}; padding: 16px 20px; margin: 16px 0; border-radius: 0 8px 8px 0;">
<div class="callout-title" style="font-weight: 600; color: {style['title_color']}; margin-bottom: 8px;">{style['icon']} {title_text}</div>
<div class="callout-content">{inner_html}</div>
</div>

'''

    return callout_pattern.sub(replace_callout, content)


def send_email(
    to: str | list[str],
    subject: str,
    html: Optional[str] = None,
    text: Optional[str] = None,
    from_email: Optional[str] = None,
    reply_to: Optional[str] = None,
) -> dict:
    """
    Send an email using Resend.

    Args:
        to: Recipient email address or list of addresses
        subject: Email subject line
        html: HTML content of the email (optional if text provided)
        text: Plain text content of the email (optional if html provided)
        from_email: Sender email address (defaults to RESEND_FROM_EMAIL env var)
        reply_to: Reply-to email address (optional)

    Returns:
        dict with 'id' of the sent email

    Raises:
        ValueError: If neither html nor text content is provided
        resend.exceptions.ResendError: If email sending fails
    """
    if not html and not text:
        raise ValueError("Either 'html' or 'text' content must be provided")

    sender = from_email or os.getenv(
        "RESEND_SOURCE_EMAIL", "onboarding@resend.dev")

    params: resend.Emails.SendParams = {
        "from": sender,
        "to": [to] if isinstance(to, str) else to,
        "subject": subject,
    }

    if html:
        params["html"] = html
    if text:
        params["text"] = text
    if reply_to:
        params["reply_to"] = reply_to

    return resend.Emails.send(params)


def send_weekly_email(
    to: str,
    review_content: str,
    week_label: str = "This Week",
) -> dict:
    """
    Send a weekly review email with formatted HTML.

    Args:
        to: Recipient email address
        review_content: The weekly review content (markdown)
        week_label: Label for the week (e.g., "Week of Jan 6")

    Returns:
        dict with 'id' of the sent email
    """
    # Parse frontmatter using python-frontmatter library
    post = frontmatter.loads(review_content)
    metadata = post.metadata
    content = post.content

    # Build stats card from metadata
    stats_card_html = build_stats_card(metadata)

    # Pre-process Obsidian callouts, then convert remaining markdown to HTML
    processed_content = convert_obsidian_callouts(content)
    md = markdown.Markdown(extensions=['tables', 'fenced_code'])
    rendered_content = md.convert(processed_content)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #1f2937;
                max-width: 640px;
                margin: 0 auto;
                padding: 24px;
                background: #f3f4f6;
            }}
            .email-container {{
                background: #ffffff;
                border-radius: 12px;
                padding: 32px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 24px;
                padding-bottom: 20px;
                border-bottom: 2px solid #e5e7eb;
            }}
            .header h1 {{
                color: #1e40af;
                font-size: 24px;
                margin: 0;
            }}
            .content h1 {{
                color: #1e40af;
                font-size: 22px;
                margin-top: 28px;
                margin-bottom: 12px;
            }}
            .content h2 {{
                color: #374151;
                font-size: 18px;
                margin-top: 24px;
                margin-bottom: 10px;
                border-bottom: 1px solid #e5e7eb;
                padding-bottom: 6px;
            }}
            .content h3 {{
                color: #4b5563;
                font-size: 16px;
                margin-top: 20px;
                margin-bottom: 8px;
            }}
            .content p {{
                margin: 12px 0;
            }}
            .content strong {{
                color: #111827;
            }}
            .content ul, .content ol {{
                margin: 12px 0;
                padding-left: 24px;
            }}
            .content li {{
                margin: 6px 0;
            }}
            .content blockquote {{
                margin: 16px 0;
                padding: 16px 20px;
                background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%);
                border-left: 4px solid #3b82f6;
                border-radius: 0 8px 8px 0;
            }}
            .content blockquote p {{
                margin: 4px 0;
            }}
            .callout-content ul {{
                margin: 8px 0;
                padding-left: 20px;
            }}
            .callout-content li {{
                margin: 4px 0;
            }}
            .callout-content p {{
                margin: 4px 0;
            }}
            .content hr {{
                border: none;
                border-top: 1px solid #e5e7eb;
                margin: 24px 0;
            }}
            .content code {{
                background: #f3f4f6;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'SF Mono', Monaco, monospace;
                font-size: 14px;
            }}
            .content pre {{
                background: #1f2937;
                color: #f9fafb;
                padding: 16px;
                border-radius: 8px;
                overflow-x: auto;
            }}
            .content table {{
                width: 100%;
                border-collapse: collapse;
                margin: 16px 0;
            }}
            .content th, .content td {{
                padding: 10px 12px;
                border: 1px solid #e5e7eb;
                text-align: left;
            }}
            .content th {{
                background: #f9fafb;
                font-weight: 600;
            }}
            .footer {{
                margin-top: 32px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                font-size: 13px;
                color: #6b7280;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>📊 Weekly Review: {week_label}</h1>
            </div>
            {stats_card_html}
            <div class="content">{rendered_content}</div>
            <div class="footer">
                Generated by Obsidian Agent ✨
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(
        to=to,
        subject=f"📊 Your Weekly Review - {week_label}",
        html=html_content,
        text=review_content,
    )


if __name__ == "__main__":
    # Test sending an email
    result = send_email(
        to="gilbertjyoungjr@gmail.com",
        subject="Test Email from Obsidian Agent",
        html="<h1>Hello!</h1><p>This is a test email.</p>",
        text="Hello! This is a test email.",
    )
    print(f"Email sent! ID: {result['id']}")
