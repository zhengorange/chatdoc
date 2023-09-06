# coding=utf-8

import configparser
import ctypes


class TokenWord(ctypes.Structure):
    _fields_ = [
        ("token", ctypes.c_int),
        ("word", ctypes.c_char * 2048)  # 假设最大长度为 100，你可以根据实际情况调整
    ]


class TPUChatglm:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.lib = ctypes.cdll.LoadLibrary(config.get('llm_model', 'libtpuchat_path'))
        device_id = 0
        bmodel_path = config.get('llm_model', 'bmodel_path')
        token_path = config.get('llm_model', 'token_path')
        self.device_id = device_id
        self.bmodel_path = bmodel_path
        self.token_path = token_path
        self.libset()
        self.init()

    def libset(self):
        self.lib.ChatGLM2_with_devid_and_model.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
        self.lib.ChatGLM2_with_devid_and_model.restype = ctypes.c_void_p

        self.lib.ChatGLM2_delete.argtypes = [ctypes.c_void_p]

        # deinit
        self.lib.ChatGLM2_deinit.argtypes = [ctypes.c_void_p]

        # ChatGLM2_predict_first_token
        self.lib.ChatGLM2_predict_first_token.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.lib.ChatGLM2_predict_first_token.restype = ctypes.c_char_p

        # ChatGLM2_predict_next_token
        self.lib.ChatGLM2_predict_next_token.argtypes = [ctypes.c_void_p]
        self.lib.ChatGLM2_predict_next_token.restype = ctypes.c_char_p

        # get_eos
        self.lib.get_eos.argtypes = [ctypes.c_void_p]
        self.lib.get_eos.restype = ctypes.c_int
        # get_history
        self.lib.get_history.argtypes = [ctypes.c_void_p]
        self.lib.get_history.restype = ctypes.c_char_p
        # set history
        self.lib.set_history.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    def init(self):
        self.obj = self.lib.ChatGLM2_with_devid_and_model(self.device_id, self.bmodel_path.encode('utf-8'),
                                                          self.token_path.encode('utf-8'))

    def predict_first_token(self, context):
        return self.lib.ChatGLM2_predict_first_token(self.obj, context.encode('utf-8')).decode('utf-8')

    def predict_next_token(self):
        return self.lib.ChatGLM2_predict_next_token(self.obj).decode('utf-8')

    def stream_predict(self, query, history):
        self.lib.set_history(self.obj, "".encode('utf-8'))
        history.append((query, ''))

        prompt = ''
        if len(history) >= 1:
            prompt += "{}\n\n答：{}\n\n".format(history[0][0], history[0][1])
            for i, (old_query, response) in enumerate(history[1:]):
                prompt += "[Round {}]\n\n问：{}\n\n答：{}\n\n".format(i + 1, old_query, response)
            prompt += "[Round {}]\n\n问：{}".format(len(history) + 1, query)
        else:
            prompt += "{}".format(query)

        res = ''
        first_token = self.predict_first_token(prompt)
        res += first_token

        while True:
            next_token = self.predict_next_token()
            if next_token == '_GETMAX_' or next_token == '_GETEOS_':
                break
            res += next_token
            history[-1] = (query, res)
            yield res, history

    def get_config(self):
        pass


if __name__ == "__main__":
    # chatglm = TPUChatglm()
    # for i in range(200):
    #     print(i)
    #     r = chatglm.predict("写一首关于春天的七言绝句。")
    #     print(r)

    # import pdb
    # pdb.set_trace()
    pass
