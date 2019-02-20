import zgoubidoo

lhec = zgoubidoo.loaders.from_madx_twiss(path='/Users/chernals/Downloads')
zgoubidoo.physics.srloss(sequence=lhec, debug=True)
