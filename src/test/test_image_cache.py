import os
import sys
import shutil
import base64

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir + '/../main/')

from cf_commands import ImageCache

BASE64_IMAGE = """
data:image/png;base64, iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAACF5JREFUeNrsXU2MFEUYre7hAKcd4ILx4CxKYkyMiyRCAskOwYMkJMwSPRHZRdR4YX88ELywiydDorvATaO7a0I8+LOzxkQ5EGYTjMGE7AiBmKAwm/jHQWhOejFYX1NNmqF7pqqnZ7qq+r2k6Qk7v/Vevfq+r6uqHWYZCkdHS/xER5kfffwYEH+ic1HybTx+1MVjOt/lR40fjf/eO9Wwqb0cCwgvC7IHFUlOikAcSyQKLogaBND7Hl4RhFc0+VokgkV+VE1zCMcw0odDlq4ryB3mTRGDoznxAekVZiaqJAYuhCoEIE96URA+KYI5G0BOcJIfc1wMHgQQT/w4P8Z6EMhlBU8IYUYXITiakD/CT9MWE6+tEJyMiaf0bdYiq08yNExkGSM4GRFfEj2+woAgjTyYRdZQyIB8Guc/MyCd6yWoQ4y7O7Y69y5crFnpACLIW2D3q3ZA6zrCUK/coNAj8on0H/jxNPhtiw38GOFucIu7Qd14AXDyp0SgtxrcSoPaqsJFUOQiOGvkECAsfxaBXipDws5upYtOF8k/j0Av1XSR4oK69gLg5A8I8ovgLVV4wgnq2goA5JsnAhfkGwVq22VROtfHAUB+JtichhO4IN9YnBdtn50DiGj/Jsg3NyZwOyQfPT/7mGBBcNHzIWAWeb4WKImOmKwjJ+z9U/z0FtpeG2xIWjYuJCC/LHo/oBe2cRGsqF5AchTJR9Cnf1C4WeVSsmoMsADy9Q8KuzIEiJk8GPfNiAekZxY5kuRTpLmM3m8U+mWGAtkhYBrkGwepQN2V6P0U9WNSh3koi6V1HTsAUj5zMd2uSui26f0jLL+LNmwAcTeeKAg0Iecf3vICO/D81tTe76c/f2fev//cf/zHb/7jpRu/2FAb6I+bU7iqxQvHdQ/8nli7ng1ufCq194t7r5U7t30hLN28zhavXnkgEoNqA8TllLQDmFLxO/bibnZs10s9/9zFa1fY19cus/lLPxrvAnExQAVpXzz2PvMs+/jl/ezXI5P+MGSIC4yoBIGToFlmCFrnC+HS6BH23GOP6/51x6QEIHJHRP4KIPLPvXlYdzcoRdUFohxgGJQm8NjVa3w30FwEwy0FENqNC0gIEkGamUnKqAiOYx0A5KeAL1993XcEXUXQqg5grf3LFnSKa9Z0HNAR+R/s2cde++KMrsPAzCMCENZg7STPXR+dViaRrHxw4yY/7aOIXwUHeCzw7rlvWePObd2aYoC4Di4Vu7D/aFC1jwo+b3/zFXvyxHF2iPfmFUUyR7eXtR8GwgIYBO3xoKrfllMn/OsFKi6gKfZGCQAOIOEKuz48Le0ENIxoWiAqPyQAMekDkBSBSnCna0oYcO42KwKQyyhkXaC0dr2uP+MhAWD871JaqfE1gsGwALDGTxEN77bpP8Hn3BX5Py795g9F4p4coIS2SDIEXLfhZ/gCQACYZADduMmGn1EmAfSBztyiz0UAmNAB+uXye80nkA64oDJB9CQuFMlApXScBeAACTC6Qz5sovUFujsAUkAFUGFndLt83UzzhSVFDAEqOdPadeyTV/ZLz/YJrzTSFatAqxxosuf7e/YpTfU69X1N+98FAbSxewr2xraXlWcE0cUiE1YO5V4A59447Ns02XWpuO4B0Z1exqWZRCYg9wIIiKZ5f2mBppLRYQIQBKYMcpJDn58x5vtCACmTT1PGTFo+jiAwJXzKAz4a9w3bOwAC6BQU7RPxpoz5UQKgTQNQDUxg95TnG7RJRBQ8EgBtLlwGpXKk+xH+1cvaX+SRRD33Q0BcrZ6sneb9rdz521/eZcFmUbFDQK4dQHXNoGWoUxp4F+aeW9wlAdTQDrlFjQTQQDvkFg1XrBP30Ba5g0fcB6XgOtojfwEg/RMIYAntkb8MOCwABII5DAAfCICPBRBAzhBw7jYrAsgFqsGDsAAW0S75Gv+bBVBFu+TYAUQ9AOlgDtK/8O3kmqeEzaN9rMdDHLtx1gDYb/+PCEBYA0RgMfnNdxN121kEYK/9RwqAK4QcoIG2sg4NwS1r5wCEk2gv63A86j/jBDDHcInYJnhxsV2kAMT95eAC9uBk3J1DWy0Nm4ELWNP7Z+L+GDstnBRTODpKLqDtPQRpyrat07VTxERc7yc4rV4pbiG7zLCbqMmRf3+rJ7RcHSyUM4F2NBYH2z2h7fJwkTvW0JbGoSoz0cdNS0mAdoGflHMXZJ5078JFz92xleKFMtrWCLzDe/93Mk90VN6VB4UUEGJnUb1R4+TvlH2y6hYxQ6gNaG/9Q0qdWuXJYii4xXCLOV2xm/f+n7smACGCOhcB1Qe2ob21wnFO/pzqi5ykn4Z4QLuUbyjJCzvZJo4CjQbaPnPUO0nTnU4+mbsAOcB5hk2msgz6+lvV+rvpAFQlrAsnQGaQDfk7OyG/YwdocoJlcNJz8jtex1FI49vwzOAvnhmsID00i/zUHAAxgZnkpy4AiMAs8jsOAtsEhkgR0031+tMmvysCCIlgM8Ni0zRQTSPa79kQEDEkTPPTOHhMBCrvTnWVn27/Ap4hnBUZQpkfq8Gp9Hi/O0ltXzsHCDlBiZ8WGK4ftEONH0PdsvzMBBASAlnaJHiO7PVk+TO9/FAni18q3GCWYYpZONCbaF66ba0AQkKgyiEFiaWcEk+EH8xymz4n6xYQi08oSxhj+SkeeaLHz2X9RRxdWiQnQggW3c70KsgzRgBNQhgRQrBlaCCrp/X5VV2I11YAETHCMDP3KiMFd/NRO3NAAOpZQyAG3esIVP6eZxEbMkEA6Yphr0ZpJPXwJVNIN1oAEYIoCyEMCnfodgDpiV5OhNdM32ndeAHEOERJiKIvNGSoiCMgObB0urMaEd0wrYe3w/8CDAAefud5jZ39uQAAAABJRU5ErkJggg==\
"""

thumbs_dir = current_dir + '/thumbs'
data_dir = current_dir + '/data'


def setup_function():
    if os.path.exists(thumbs_dir):
        shutil.rmtree(thumbs_dir)
    os.makedirs(thumbs_dir)


def teardown_function():
    if os.path.exists(thumbs_dir):
        shutil.rmtree(thumbs_dir)


def test_an_image_can_be_built_from_url():
    params = dict()

    def url_loader(actual_url, actual_file_path):
        params['url'] = actual_url
        params['file_path'] = actual_file_path

    cache = ImageCache(base_directory=thumbs_dir, url_loader=url_loader)
    cache.load_image('123', 'http://somewebsite/picture.png')
    assert params['file_path'] == thumbs_dir + '/123.png'
    assert params['url'] == 'http://somewebsite/picture.png'


def test_a_base64_image_can_be_built():
    cache = ImageCache(base_directory=thumbs_dir)
    cache.load_image('123', BASE64_IMAGE.strip())
    assert os.path.isfile(thumbs_dir + '/123.png')


def test_an_existing_image_is_directly_returned_from_filesystem():
    shutil.copyfile(data_dir + '/sample.png', thumbs_dir + '/sample.png')

    cache = ImageCache(base_directory=thumbs_dir)
    cache.load_image('sample', "totally different")

    with(open(data_dir + '/sample.png', 'rb')) as f:
        expected_content = f.read()
        expected_base64 = base64.b64encode(expected_content).decode('ascii')

    with(open(thumbs_dir + '/sample.png', 'rb')) as f:
        content = f.read()
        actual_base64 = base64.b64encode(content).decode('ascii')

    assert expected_base64 == actual_base64
