import textwrap
import unicodedata
from itertools import groupby

MAXWIDTH = 70


# copy from docutils
def column_width(text):
    """Return the column width of text.

    Correct ``len(text)`` for wide East Asian and combining Unicode chars.
    """
    combining_correction = sum([-1 for c in text if unicodedata.combining(c)])
    width = len(text)
    return width + combining_correction


class TextWrapper(textwrap.TextWrapper):
    """Custom subclass that uses a different word splitter."""

    def _wrap_chunks(self, chunks):
        """_wrap_chunks(chunks : [string]) -> [string]

        Original _wrap_chunks use len() to calculate width.
        This method respect to wide/fullwidth characters for width adjustment.
        """
        lines = []
        if self.width <= 0:
            raise ValueError("invalid width %r (must be > 0)" % self.width)

        chunks.reverse()

        while chunks:
            cur_line = []
            cur_len = 0

            indent = self.subsequent_indent if lines else self.initial_indent

            width = self.width - column_width(indent)

            if self.drop_whitespace and chunks[-1].strip() == "" and lines:
                del chunks[-1]

            while chunks:
                ll = column_width(chunks[-1])
                if cur_len + ll <= width:
                    cur_line.append(chunks.pop())
                    cur_len += ll
                else:
                    break

            if chunks and column_width(chunks[-1]) > width:
                self._handle_long_word(chunks, cur_line, cur_len, width)

            if self.drop_whitespace and cur_line and cur_line[-1].strip() == "":
                del cur_line[-1]

            if cur_line:
                lines.append(indent + "".join(cur_line))

        return lines

    def _break_word(self, word, space_left):
        """_break_word(word : string, space_left : int) -> (string, string)

        Break line by unicode width instead of len(word).
        """
        total = 0
        for i, c in enumerate(word):
            total += column_width(c)
            if total > space_left:
                return word[: i - 1], word[i - 1 :]
        return word, ""

    def _split(self, text):
        """_split(text : string) -> [string]

        Override original method that only split by 'wordsep_re'.
        This '_split' split wide-characters into chunk by one character.
        """

        def split(t):
            return textwrap.TextWrapper._split(self, t)

        chunks = []
        for chunk in split(text):
            for w, g in groupby(chunk, column_width):
                if w == 1:
                    chunks.extend(split("".join(g)))
                else:
                    chunks.extend(list(g))
        return chunks

    def _handle_long_word(self, reversed_chunks, cur_line, cur_len, width):
        """_handle_long_word(chunks : [string],
                             cur_line : [string],
                             cur_len : int,
                             width : int)

        Override original method for using self._break_word() instead of slice.
        """
        space_left = max(width - cur_len, 1)
        if self.break_long_words:
            ll, rr = self._break_word(reversed_chunks[-1], space_left)
            cur_line.append(ll)
            reversed_chunks[-1] = rr

        elif not cur_line:
            cur_line.append(reversed_chunks.pop())


def fw_wrap_vi(text, width=MAXWIDTH, **kwargs):
    w = TextWrapper(width=width, **kwargs)
    return w.wrap(text)


def fw_fill_vi(text, width=MAXWIDTH, **kwargs):
    w = fw_wrap_vi(text=text, width=width, **kwargs)
    return "\n".join(w)
