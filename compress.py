import bz2
import base64

def compress_text_file(input_file, output_file):
    """
    Compresses a text file using bz2 compression and encodes the compressed data in base64.
    
    Args:
        input_file (str): Path to the input text file to be compressed.
        output_file (str): Path to the output file where the compressed data will be written.
    """
    with open(input_file, 'rb') as f_in:
        data = f_in.read()

    compressed_data = bz2.compress(data)
    base64_compressed_data = base64.b64encode(compressed_data).decode('utf-8')

    with open(output_file, 'w', encoding='utf-8') as f_out:
        f_out.write(base64_compressed_data)

if __name__ == '__main__':
    input_file = 'fullsource.txt'
    output_file = 'fullsource_compressed.txt'
    compress_text_file(input_file, output_file)