try:
    from wise.translators.pure_wrap import PureInterface
except ImportError:
    raise Exception('Could not load Cython Pure module, perhaps it needs to be built?')
