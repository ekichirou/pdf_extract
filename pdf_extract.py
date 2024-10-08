import sys
import os
from pdf2image import convert_from_path
from PIL import Image
import fitz 
from argparse import ArgumentParser

def convert_pdf_to_jpeg(pdf_path, output_folder):
    images = convert_from_path(pdf_path)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for i, image in enumerate(images):
        image_filename = os.path.join(output_folder, f'page_{i + 1}.jpeg')
        image.save(image_filename, 'JPEG')
        print(f"[+] Page converted to: {image_filename}")

def extract_hyperlinks(pdf_path):
    document = fitz.open(pdf_path)
    all_links = []
    for page in document:
        link_list = page.get_links()
        text_instances = page.get_text("dict")['blocks']

        for link in link_list:
            if link['kind'] == fitz.LINK_URI:
                link_rect = fitz.Rect(link['from'])
                link_text = ''

                for text_instance in text_instances:
                    if 'lines' in text_instance:
                        for line in text_instance['lines']:
                            for span in line['spans']:
                                span_rect = fitz.Rect(span['bbox'])
                                if link_rect.intersects(span_rect):
                                    link_text += span['text'] + ' '

                link_text = link_text.strip()
                if link_text:
                    all_links.append(f"[{link_text}] {link['uri']}")
                else:
                    all_links.append(f"[URL] {link['uri']}")

    document.close()
    return all_links

def convert_jpeg_to_pdf(image_folder, output_pdf):
    images = sorted(
        [os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith('.jpeg')],
        key=lambda x: os.path.basename(x)
    )
    imgs = [Image.open(img).convert("RGB") for img in images]
    imgs[0].save(output_pdf, save_all=True, append_images=imgs[1:])
    print(f"[+] Images converted to: {output_pdf}")

def main():
    parser = ArgumentParser(description="Convert PDF to JPEG, extract URLs and re-convert JPEG to PDF")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_conv = subparsers.add_parser('conv', help='Convert PDF to JPEG and extract URLs')
    parser_conv.add_argument("-pdf", "--pdf_path", required=True, help="Path to the PDF file to convert")
    parser_conv.add_argument("-out", "--output_folder", required=True, help="Folder to save the output JPEG images")

    parser_reconv = subparsers.add_parser('reconv', help='Re-convert JPEG to PDF')
    parser_reconv.add_argument("-img", "--image_folder", required=True, help="Folder containing JPEG images")
    parser_reconv.add_argument("-pdf", "--output_pdf", required=True, help="Path to save the output PDF file")

    args = parser.parse_args()

    if args.command == 'conv':
        convert_pdf_to_jpeg(args.pdf_path, args.output_folder)
        links = extract_hyperlinks(args.pdf_path)
        links_filename = os.path.join(args.output_folder, f'{args.pdf_path}_extracted_urls.txt')
        with open(links_filename, 'w') as file:
            for link in links:
                file.write(link + '\n')
        print(f"[+] URLs extracted to: '{links_filename}'.")

    elif args.command == 'reconv':
        convert_jpeg_to_pdf(args.image_folder, args.output_pdf)

if __name__ == "__main__":
    main()
