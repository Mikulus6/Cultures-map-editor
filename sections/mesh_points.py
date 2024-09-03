def combine_mep(mepa, mepb):
    mep = b""
    for index in range(len(mepa)):
        mep += mepa[2 * index: 2 * index + 2]
        mep += mepb[2 * index: 2 * index + 2]
    return mep


def split_mep(mep):
    mepa = b""
    mepb = b""

    for index in range(len(mep) // 2):
        if index % 2 == 0:
            mepa += mep[2 * index: 2 * index + 2]
        else:
            mepb += mep[2 * index: 2 * index + 2]

    return mepa, mepb
