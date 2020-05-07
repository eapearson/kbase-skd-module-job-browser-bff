import sys
import re

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: fix-impl <impl file>")
        sys.exit(1)

    impl_file_path = sys.argv[1]
    print(f"Fixing impl file {impl_file_path}")
    with open(impl_file_path, 'r') as file:
        text = file.read()

    # print('fixing', text)

    with open(impl_file_path, 'w') as file:
        fixed_text = re.sub(r'(# END .*$)([\s\S]*?)([\n]    def)',
                            r'\1\n\3', text, flags=re.MULTILINE)
        fixed_text2 = re.sub(r'(# END_STATUS\n).*$',
                             r'\1', fixed_text, flags=re.MULTILINE)
        # print('fixed?', fixed_text)
        file.write(fixed_text2)
