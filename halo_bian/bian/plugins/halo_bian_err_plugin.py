
class BianPlugin():

    def ready(self):
        return True

    def run(self,core,*params):
        err = "from halo_bian.bian.mixin_err_msg import ErrorMessages\n\n"
        return {"err":err}


