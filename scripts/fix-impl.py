# fix-impl.py
# Apply improvements to the impl file generated by kb-sdk.

import re

# TODO: remove return check for methods - since we are using validation, it is not necessary.
# TODO: can we improve the method docstring?

def remove_return_check(impl_text):
    return_check_re = re.compile('# At some point might do deeper type checking[.]{3}.*?# return the results', re.DOTALL|re.MULTILINE)
    return re.sub(return_check_re, '', impl_text)

def fix_impl():
    impl_file_path = 'lib/JobBrowserBFF/JobBrowserBFFImpl.py'
    with open(impl_file_path, 'r+') as impl_file:
        impl_file_content = impl_file.read()
        fixed = remove_return_check(impl_file_content)
        if fixed != impl_file_content:
            impl_file.seek(0)
            impl_file.write(fixed)
            impl_file.truncate()

fix_impl()