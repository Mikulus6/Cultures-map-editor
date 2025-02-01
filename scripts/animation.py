from PIL import Image
from scripts.buffer import BufferGiver, BufferTaker
from supplements.remaptables import RemapTable


def get_bounding_rectangle(rects):
    rects_generated = tuple(rects)

    if len(rects_generated) == 0:
        return 0, 0, 1, 1

    min_x = min(x for x, _, _, _ in rects_generated)
    min_y = min(y for _, y, _, _ in rects_generated)
    max_x = max(x + w for x, _, w, _ in rects_generated)
    max_y = max(y + h for _, y, _, h in rects_generated)
    return min_x, min_y, max_x - min_x, max_y - min_y


class Animation:
    """Objects from this class stores extracted animation of landscapes with proper rect bounds."""
    def __init__(self, images = tuple(), rect = (0, 0, 0, 0)):
        self.images = list(images)
        self.rect = rect

    def save(self, filename: str, *, frame_duration=0.1):
        assert (filename.lower()).endswith(".webp")
        # Note that unlike other popular file formats (like *.png and *.gif), *.webp is one of the few of them which
        # supports both alpha channel and animations. That's why it's used here instead of other more popular formats.

        if len(self.images) > 1:
            self.images[0].save(filename, save_all=True, append_images=self.images[1:],
                                duration=frame_duration*1000, loop=0, format="WEBP", lossless=True)
        elif len(self.images) == 1:
            self.images[0].save(filename, save_all=True)
        else:
            raise IndexError

    def __getitem__(self, item):
        assert isinstance(item, int) and 0 <= item < len(self.images)
        return self.images[item]

    def __len__(self):
        return len(self.images)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return tuple(self.rect) == tuple(other.rect) and tuple(self.images) == tuple(other.images)

    # Following two methods do not correspond to any binary data present in game files. This is merely a project
    # convention for storing animations as bytes.

    def __bytes__(self):
        buffer_taker = BufferTaker()
        for rect_element in self.rect:
            buffer_taker.signed(rect_element, length=4)
        buffer_taker.unsigned(len(self.images), length=4)
        for image in self.images:
            buffer_taker.bytes(image.tobytes())
        return bytes(buffer_taker)

    @classmethod
    def from_bytes(cls, bytes_obj: bytes):
        animation = cls()
        buffer = BufferGiver(bytes_obj)
        animation.rect = (buffer.signed(length=4),
                          buffer.signed(length=4),
                          buffer.signed(length=4),
                          buffer.signed(length=4))
        for _ in range(buffer.unsigned(length=4)):
            animation.images.append(Image.frombytes(mode="RGBA",
                                                    size=animation.rect[2:],
                                                    data=buffer.bytes(animation.rect[2] * animation.rect[3] * 4)))
        return animation

    def from_bitmap_dict(self, bitmap_dict, remaptable: RemapTable = None, shading_factor = 255,
                         first_bob = 0, elements = 1, high_color_shading_mode = 0, masked_file: bool = False):

        rects = []
        for frame_index in range(first_bob, first_bob + elements):
            try:
                rects.append(bitmap_dict[frame_index].rect)
            except KeyError:
                pass

        self.rect = get_bounding_rectangle(rects)
        if self.rect[2:] == (0, 0):
            self.rect = (*self.rect[:2], 1, 1)

        self.images = []
        for frame_index in range(first_bob, first_bob + elements):
            frame_image = Image.new("RGBA", size=self.rect[2:], color=(0, 0, 0, 0))
            try:
                frame = bitmap_dict[frame_index]
                frame_image.paste(frame.to_image(remaptable=remaptable, shading_factor=shading_factor,
                                                 high_color_shading_mode=high_color_shading_mode,
                                                 masked_file=masked_file),
                                  (frame.rect[0] - self.rect[0], frame.rect[1] - self.rect[1]))
            except KeyError:
                pass
            self.images.append(frame_image)

    def paste(self, other):
        assert isinstance(other, self.__class__)
        assert len(self.images) == len(other.images)

        old_rect = self.rect
        self.rect = get_bounding_rectangle((self.rect, other.rect))

        for index_value, other_image in enumerate(other.images):
            old_image = self.images[index_value]
            self.images[index_value] = Image.new("RGBA", size=self.rect[2:], color=(0, 0, 0, 0))
            self.images[index_value].alpha_composite(old_image, (old_rect[0] - self.rect[0],
                                                                 old_rect[1] - self.rect[1]))
            self.images[index_value].alpha_composite(other_image, (other.rect[0] - self.rect[0],
                                                                   other.rect[1] - self.rect[1]))

    @classmethod
    def empty(cls):
        return cls(images=[Image.new("RGBA", size=(1, 1), color=(0, 0, 0, 0))], rect=(0, 0, 1, 1))
