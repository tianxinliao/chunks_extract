class ConlluWriter:
    def __init__(self, sent_id, sent_text, sent_attrs):
        self.sent_id = sent_id
        self.sent_text = sent_text
        self.sent_attrs = sent_attrs
        self.output_text = ""

    def format_output(self):
        sent_head = ""
        sent_head += f"# sent_id = {self.sent_id}\n"
        sent_head += f"# text = {self.sent_text}\n"
        attrs = '\t'.join(list(self.sent_attrs[0].keys()))
        sent_head += f"# attrs = {attrs}\n"
        self.output_text += sent_head
        for word_attrs in self.sent_attrs:
            word_content = "\t".join(word_attrs.values())
            self.output_text += f"{word_content}\n"
        self.output_text += "\n" 

    def show_output(self):
        return self.output_text

    def write_file(self, fw):
        fw.write(self.output_text)


class Word(dict):
    def __init__(self, word):
        super(Word, self).__init__()
        self.attrib = word

    def __str__(self):
        return "<Element Word>"


class Sent(list):
    def __init__(self, conllu_text):
        super(Sent, self).__init__()
        self.conllu = conllu_text
        # self.sent = []
        self.conv_conllu()


    def conv_conllu(self):
        for line in self.conllu.split("\n"):
            if not line:
                continue
            if line.startswith("# "):
                if line.startswith("# attrs"):
                    attrs_head = line.lstrip("# attrs = ").split("\t")
            else:
                attrs = line.split("\t")
                word_attrs = dict(zip(attrs_head, attrs))
                word = Word(word_attrs)
                self.append(word)
        
