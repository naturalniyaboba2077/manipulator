from idlelib.iomenu import errors


class Log():
    def __init__(self):
        self.logs = []
        self.errors = []


    def add_logs(self, logs): 
        self.logs.append(logs)


    def add_errors(self, errors):
        self.errors.append(errors)
        self.logs.append(errors)

    def get_logs(self):
        logss = ""
        for i in self.logs:
            logss+= i
            logss+= "\n"
        return logss

    def get_errors(self):
        errorss = ""
        for i in self.errors:
            errorss+= i
            errorss+= "\n"
        return errorss




log = Log()


log.add_logs("оно запустилось")
log.add_errors("всем пизда")

print(log.get_logs())


