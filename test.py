import fast_io

file = "C:\FAST\CertTest\Test18_mod3b.outb"

data, info, pack = fast_io.load_binary_output(file)
print(info['attribute_names'])