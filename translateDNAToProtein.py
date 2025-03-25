#!/usr/bin/env python3
import sys

def translate_dna_to_protein(dna_sequence):
    """
    Translate a DNA sequence into a protein sequence using the standard genetic code.
    Args:
        dna_sequence (str): DNA sequence to be translated (5' to 3')
    Returns:
        str: Protein sequence
    """
    genetic_code = {
        'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
        'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
        'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K',
        'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',
        'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
        'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
        'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q',
        'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
        'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V',
        'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
        'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E',
        'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
        'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
        'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
        'TAC':'Y', 'TAT':'Y', 'TAA':'*', 'TAG':'*',
        'TGC':'C', 'TGT':'C', 'TGA':'*', 'TGG':'W'
    }
    
    protein_sequence = []
    dna_sequence = dna_sequence.upper()
    
    # Remove any whitespace or unexpected characters
    dna_sequence = ''.join([c for c in dna_sequence if c in 'ATCG'])
    
    # Check if sequence is empty after cleaning
    if not dna_sequence:
        return ''
    
    # Iterate over the DNA sequence in steps of 3
    for i in range(0, len(dna_sequence) - 2, 3):
        codon = dna_sequence[i:i+3]
        amino_acid = genetic_code.get(codon, 'X')  # 'X' for unknown codons
        protein_sequence.append(amino_acid)
    
    return ''.join(protein_sequence)

def process_file(input_file, column_num, output_file):
    """
    Process the input file and add protein translation column
    Args:
        input_file (str): Path to input file
        column_num (int): Column index containing DNA sequences (0-based)
        output_file (str): Path to output file
    """
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                
                fields = line.split('\t')
                try:
                    dna_seq = fields[column_num]
                    protein_seq = translate_dna_to_protein(dna_seq)
                    new_line = line + '\t' + protein_seq + '\n'
                    outfile.write(new_line)
                except IndexError:
                    print(f"Warning: Line doesn't have column {column_num}: {line}")
                    outfile.write(line + '\t\n')  # Write original line with empty protein column
    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
        sys.exit(1)

def main():
    if len(sys.argv) != 4:
        print("Usage: python translateDNAToProtein.py <input_file> <column_number> <output_file>")
        #print("Note: Column numbers are 0-based (first column is 0)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    try:
        column_num = int(sys.argv[2])-1
    except ValueError:
        print("Error: Column number must be an integer")
        sys.exit(1)
    
    output_file = sys.argv[3]
    
    process_file(input_file, column_num, output_file)
    print(f"Translation complete. Results written to {output_file}")

if __name__ == "__main__":
    main()
