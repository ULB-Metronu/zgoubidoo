import zgoubidoo
from zgoubidoo.commands import Dipoles

_ = zgoubidoo.ureg

d = Dipoles('TEST',
        BI=[[1, 2 ,3 ,4 ,5]])
str(d)
str(d)