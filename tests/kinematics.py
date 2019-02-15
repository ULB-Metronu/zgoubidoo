"""Test of the kinematics module"""
import zgoubidoo

k = zgoubidoo.kinematics.Kinematics(60 * zgoubidoo.ureg.GeV, particle=zgoubidoo.commands.Electron)
k.beta