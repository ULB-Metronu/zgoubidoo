from . import Q_


def _m(q: Q_) -> float:
    return q.to('m').magnitude


def _cm(q: Q_) -> float:
    return q.to('cm').magnitude


def _degree(q: Q_) -> float:
    return q.to('degree').magnitude


def _radian(q: Q_) -> float:
    return q.to('radian').magnitude


def _tesla(q: Q_) -> float:
    return q.to('tesla').magnitude


def _gauss(q: Q_) -> float:
    return q.to('gauss').magnitude


def _kilogauss(q: Q_) -> float:
    return q.to('kilogauss').magnitude
