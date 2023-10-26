import os
from dotenv import load_dotenv
from imapclient import IMAPClient
from email import message_from_bytes
from email.header import decode_header
import html
import html2text

load_dotenv()

HOST = os.getenv('IMAP_HOST')
USERNAME = os.getenv('IMAP_USERNAME')
PASSWORD = os.getenv('IMAP_PASSWORD')

def connect_to_imap_server(host, username, password):
    client = IMAPClient(host)
    client.login(username, password)
    return client

def list_all_mailboxes(client):
    return [mailbox_name for flags, delimiter, mailbox_name in client.list_folders()]

def get_latest_email(client, folder='INBOX'):
    client.select_folder(folder)
    messages = client.search(['NOT', 'DELETED'])
    if messages:
        latest_email_id = messages[-1]
        return client.fetch([latest_email_id], ['BODY[]', 'FLAGS'])
    return None

def get_decoded_header(email_message, header_name):
    header_value = email_message[header_name]
    if header_value:
        decoded_header = decode_header(header_value)[0]
        return decoded_header[0]
    return None

def is_plain_text(part):
    content_type = part.get_content_type()
    content_disposition = str(part.get('Content-Disposition'))
    return content_type == 'text/plain' and 'attachment' not in content_disposition

def is_html_text(part):
    content_type = part.get_content_type()
    content_disposition = str(part.get('Content-Disposition'))
    return content_type == 'text/html' and 'attachment' not in content_disposition

def extract_text_from_part(part):
    return part.get_payload(decode=True).decode(part.get_content_charset())

def convert_html_to_plain_text(html_content):
    # Basic conversion from HTML to text
    return html.unescape(" ".join(html_content.splitlines()).replace('<', ' <'))

def get_text_from_email(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if is_plain_text(part):
                return extract_text_from_part(part)
            elif is_html_text(part):
                html_content = extract_text_from_part(part)
                return convert_html_to_plain_text(html_content)
        
        # If no suitable part found, return an empty string
        return ""
    else:
        content = extract_text_from_part(msg)
        if msg.get_content_type() == 'text/html':
            return convert_html_to_plain_text(content)
        return content

def convert_html_to_text(html_string):
    h = html2text.HTML2Text()
    # Customize the conversion if necessary
    # For example, to ignore links, you can set: h.ignore_links = True
    return h.handle(html_string)

def print_email_details(from_address, to_address, date, subject, content):
    print(f"From: {from_address}")
    print(f"To: {to_address}")
    print(f"Date: {date}")
    print(f"Subject: {subject}")
    print("\nMessage:")
    print(content)

def main():
    with connect_to_imap_server(HOST, USERNAME, PASSWORD) as client:
        for mailbox in list_all_mailboxes(client):
            print(mailbox)
        
        raw_message = get_latest_email(client)
        if raw_message:
            email_data = raw_message[list(raw_message.keys())[0]][b'BODY[]']
            email_message = message_from_bytes(email_data)

            from_address = get_decoded_header(email_message, 'From')
            to_address = get_decoded_header(email_message, 'To')
            date = get_decoded_header(email_message, 'Date')
            subject = get_decoded_header(email_message, 'Subject')
            content = get_text_from_email(email_message)
            text = convert_html_to_text(content)

            print_email_details(from_address, to_address, date, subject, text)
        
        client.logout()

if __name__ == '__main__':
    main()
