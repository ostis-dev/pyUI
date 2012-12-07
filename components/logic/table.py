class table:
    __information = "logic_gram.g"
    def __init__(self,information):
        self.__information=information
    def makeTextTable(self):
        table=self.genereteDisk()
        maxSize=0
        for var in table['var']:
            if maxSize<len(var):
                maxSize=len(var)
        result=self.getOneLine(table['var'],maxSize)+"\n"
        line=self.getHorizontalLine(len(result))+"\n"
        result=line+result+line
        for variant in table['variants']:
            line=self.getOneLine(variant,maxSize);
            result=result+line+"\n"
            result=result+self.getHorizontalLine(len(line))+"\n"
        return result
    def getHorizontalLine(self,length):
        result=""
        for i in range(length):
            result=result+"_"
        return result
    def getOneLine(self,list,maxSize):
        result=""
        for var in list:
            result=result+"|"
            center=maxSize/2+1;
            tab=center-len(var)/2
            for i in range(tab):
                result=result+" "
            result=result+var
            for i in range(tab):
                result=result+" "
        return result+"|"

    def genereteDisk(self):
        disc = {'var': ['x', 'y','z', "x&y", "x&y|z"]}
                            # x  y   z  x&y x&y|z
        disc['variants'] = [["0","0","0","0","0"],
                            ["0","0","1","0","1"],
                            ["0","1","0","0","0"],
                            ["0","1","1","0","1"],
                            ["1","0","0","0","0"],
                            ["1","0","1","0","1"],
                            ["1","1","0","1","1"],
                            ["1","1","1","1","1"]
        ]
        return disc