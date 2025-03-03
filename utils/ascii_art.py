class ASCIIArtConverter:
    def __init__(self, gradient=" .,:;irsXA253hMHGS#9B&@"):
        self.gradient = list(gradient)
        self.gradient_length = len(self.gradient)  # Исправлено здесь

    def convert_frame(self, normalized_frame):
        return "\n".join(
            "".join(
                self.gradient[
                    min(int(p * (self.gradient_length - 1)), self.gradient_length - 1)
                ]
                for p in row
            )
            for row in normalized_frame
        )
