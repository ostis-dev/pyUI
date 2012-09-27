class ScaleManager:
    factors = [1, 1, 1.3, 1.6, 2, 2.5, 3, 3.5, 4, 5, 8, 12, 16, 20, 1/16, 1/8, 1/4, 1/3, 1/2]
    DRAW_OBJECT = 101
    DRAW_TEXT = -101
    DIR_ASC = 1
    DIR_DESC = 2

class DrawingRule:
    def __init__(self, attributeName, startScale, threshold = 0, 
                 direction = ScaleManager.DIR_ASC, textRule = False, comparator = None):
        self.threshold = threshold
        self.attributeName = attributeName
        self.textRule = textRule
        self.startScale = startScale
        self.direction = direction
        self.comparator = comparator
        
    def __str__(self):
        s = "<Rule "
        if self.textRule:
            s += "(TEXT) "
        s += ": attribute: " + str(rule.attributeName) + ": value: " + str(rule.threshold)
        if self.direction == ScaleManager.DIR_DESC:
            s += "+"
        else:
            s+= "-"
        s += ", scale: " + str(rule.startScale) + ">"
        
        return s
    
rule = DrawingRule("F38", 3, 5000, ScaleManager.DIR_ASC, textRule = True)
print rule
