"""
This file contains lists used by the Flask application.
They are stored here for neatness
"""

# FILE TYPE UPLOADS ALLOWED BY SERVER
ALLOWED_EXTENSIONS = {
    'fasta',
}

# TYPES OF TEXT INPUT ACCEPTED BY COLLECTION CREATION FORM
INPUT_TYPES = (
    (0, 'FASTA'),
)

# AMINO ACID CHOICES FOR MOTIF BUILDER FORM
AMINOACID_CHOICES = (
    ('G', 'G - Glycine'),
    ('A', 'A - Alanine'),
    ('L', 'L - Leucine'),
    ('M', 'M - Methionine'),
    ('F', 'F - Phenylalanine'),
    ('W', 'W - Tryptophan'),
    ('K', 'K - Lysine'),
    ('Q', 'Q - Glutamine'),
    ('E', 'E - Glutamic Acid'),
    ('S', 'S - Serine'),
    ('P', 'P - Proline'),
    ('V', 'V - Valine'),
    ('I', 'I - Isoleucine'),
    ('C', 'C - Cysteine'),
    ('Y', 'Y - Tyrosine'),
    ('H', 'H - Histidine'),
    ('R', 'R - Arginine'),
    ('N', 'N - Asparagine'),
    ('D', 'D - Aspartic Acid'),
    ('T', 'T - Threonine')
)
