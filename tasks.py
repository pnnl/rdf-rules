pkg = 'rdf_rules'

def get_rev():
    from subprocess import check_output as run
    return run('git rev-parse --abbrev-ref HEAD', text=True).strip()
rev = get_rev()


def build(update=True, commit=False, ):
    def run(cmd, *p, **k):
        from subprocess import check_call as run
        from pathlib import Path
        return run(cmd, *p, cwd=Path(__file__).parent, **k)
    if update:
        run(f'uv version {ver(increment=True)}', )
        # https://github.com/pre-commit/pre-commit/issues/747#issuecomment-386782080
        # will update uv.lock
    if commit:
        run('git add -u', )
    run('uv build')


def ver(*,increment=False):
    from datetime import datetime as dt
    dt = dt.now()
    mjr = str(dt.year)
    mnr = str(dt.month)
    pch = str(ncommits()+(1 if increment else 0))
    return f"{mjr}.{mnr}.{pch}"
def ncommits(rev=rev):
    from subprocess import check_output as run
    c = run(f'git rev-list --count {rev}', text=True).strip()
    return int(c)



if __name__ == '__main__':
    from fire import Fire
    Fire({f.__name__:f for f in {build, }})
