from signal import Signal

example = Signal("/hello", {
    "message": "Hello World"
})

encoded = bytes(example)


decoded = Signal.decode(encoded)
dec_path = decoded.path
dec_data = decoded.data

print(dec_path, dec_data)
