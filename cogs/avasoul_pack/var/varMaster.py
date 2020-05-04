from .varSys import varSys
from .varItem import varItem



class varMaster:
    def __init__(self):
        """
            Each var class should have their own reload method, with two options: Single/Multiple, All.
        """
    
        # varSys
        if not hasattr(varSys, 'reloader'):
            self.varSys = varSys(reloader=self.reloader)
        # varItem
        if not hasattr(varItem, 'reloader'):
            self.varItem = varItem(reloader=self.reloader)



    def reload(self, branchName, varNames):
        """
            branchName      (String)        Name of the branch.

            varNames        (String)        Names of variables (format=="name" or "name-defaultValue")

            Note:

            + boolean variable should be given default var.
        """

        try:
            o = getattr(self, branchName)
        except AttributeError:
            print("<!> varMaster: Branch not found (name={})".format(branchName))
            return False

        temp = []
        for i in varNames.split(' '):
            temp.append(i.split('-'))

        o.reloader(varNames, defaulting=self.defaulting)



    def reloader(self, varNames, defaulting=None, branchName=''):
        """
            varNames        (Iterable)        Namess of variables (format==[name] or [name, defaultValue])
        """

        for a in varNames:
            try:
                try:
                    setattr(self, a[0], defaulting(getattr(self, a[0]), defaultVal=a[1]))
                except IndexError:
                    setattr(self, a[0], defaulting(getattr(self, a[0])))
            except AttributeError:
                print("<!> Var not found! (branch='{}'  |  var='{}')".format(branchName, a[0]))

    def defaulting(self, varIn, defaultVal=None):
        if isinstance(varIn, int):
            return defaultVal if defaultVal else 0
        if isinstance(varIn, str):
            return defaultVal if defaultVal else ''
        if isinstance(varIn, bool):
            return defaultVal if defaultVal else False
