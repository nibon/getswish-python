import nox  # noqa


@nox.session(python=["3.10", "3.11", "3.12"])
def tests(session):
    session.run("pip", "install", "-e", ".[tests]", silent=True)
    session.run("pytest")


@nox.session
def coverage(session):
    session.run("pip", "install", "-e", ".[tests]", silent=True)
    session.run("pytest", "--cov=src")
