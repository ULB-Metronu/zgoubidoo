import zgoubidoo

lhec = zgoubidoo.converters.from_madx_twiss(path='/Users/chernals/Downloads')
zgoubidoo.physics.srloss(sequence=lhec, debug=True)
