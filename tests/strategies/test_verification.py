
def test_formal_step(self, enum_verified):
    raise NotImplementedError

def test_verification_rule(self, enum_verified, enum_not_verified):
    assert isinstance(enum_verified.verification_rule(), VerificationRule)
    assert (
        enum_verified.verification_rule().formal_step == enum_verified.formal_step
    )
    assert enum_not_verified.verification_rule() is None



def test_formal_step(self, enum_verified):
    assert enum_verified.formal_step == "Base cases"




def test_formal_step(self, enum_verified):
    assert enum_verified.formal_step == "Tiling is locally factorable"



def test_formal_step(self, enum_verified):
    assert enum_verified.formal_step == "Tiling is locally enumerable"


def test_formal_step(self, enum_verified):
    assert enum_verified.formal_step == "Tiling is a monotone tree"



def test_formal_step(self, enum_verified):
    assert enum_verified.formal_step == "Tiling is elementary"


def test_formal_step(self, enum_verified):
    assert enum_verified.formal_step == "Tiling is in the database"


def test_formal_step(self, enum_verified):
    assert (
        enum_verified.formal_step
        == "This tiling is a subclass of the original tiling."
    )
