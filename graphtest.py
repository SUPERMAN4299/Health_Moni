import random
import time

class RandomValueWriter:
    def __init__(self, filename):
        self.filename = filename

    def generate_value(self):
        """Generate a random integer between 0 and 100"""
        return random.randint(0, 100)

    def write_to_file(self, value):
        """Write a single random value to the file"""
        with open(self.filename, "a") as file:
            file.write(f"{value}\n")
        print(f"Written value: {value}")

    def start_writing(self, interval=1):
        """Continuously generate and write random values"""
        print(f"Writing random values to '{self.filename}' every {interval} second(s)...")
        while True:
            value = self.generate_value()
            self.write_to_file(value)
            time.sleep(interval)

if __name__ == "__main__":
    writer = RandomValueWriter("BPM_data.txt")
    writer.start_writing(interval=1)
