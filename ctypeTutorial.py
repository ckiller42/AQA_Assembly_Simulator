import ctypes
import multiprocessing
from multiprocessing import Process

# C only accept byte array for string
# Create mutable string array
# strPar = ctypes.create_string_buffer(100)
# strPar.value = b"Hello World"
def worder():
    clibrary = ctypes.CDLL("./components/test.so")

    alloc_func = clibrary.alloc_memory
    alloc_func.restype = ctypes.POINTER(ctypes.c_char_p)
    free_func = clibrary.free_memory
    free_func.argtypes = [ctypes.POINTER(ctypes.c_char_p)]

    cstring_pointer = alloc_func()

    cstring = ctypes.c_char_p.from_buffer(cstring_pointer)
    print(cstring.value)
    # Have to pass in the pointer
    free_func(cstring_pointer)

    num = ctypes.c_int(100)
    ptr = ctypes.pointer(num)
    print(ptr.contents)

    ptr2 = ctypes.POINTER(ctypes.c_int)
    ptr2.contents = num


def worker():
    clibrary = ctypes.CDLL("./components/test.so")

    values = (ctypes.c_int * 10)()
    for i in range(len(values)):
        values[i] = i

    clibrary.getArray.restype = ctypes.POINTER(ctypes.c_int)
    res = clibrary.getArray()
    print(res)
    for i in range(10):
        print(res[i])
    mylist = res[:10]
    print(mylist)
    t = ctypes.c_int(8)
    print(t)

    # Do sth here
    # Once the use of array is done
    # Free the memory
    clibrary.free_array(res)


class Point(ctypes.Structure):
    # Tuple: (Variable name, variable type)
    _fields_ = [("x", ctypes.c_int),
                ("y", ctypes.c_int)]


class PointArray(ctypes.Structure):
    _fields_ = [("points", Point * 3)]


class Student(ctypes.Structure):
    _fields_ = [("name", ctypes.c_char_p)]


def workstruct():
    clibrary = ctypes.CDLL("./components/test.so")
    # get = clibrary.getPoint
    # get.restype = ctypes.POINTER(Point)
    # p = get()
    # name = "Legacy"
    # s = Student(bytes(name, "utf-8"))
    # clibrary.getStudent.restype = ctypes.POINTER(Student)
    # s = clibrary.getStudent()
    # print(s)
    # print(s.contents.name)
    # print(p.contents.x, p.contents.y)
    # structP = Point(5, 10)
    # p = ctypes.pointer(structP)
    # # test = ctypes.pointer(ctypes.c_int(10))
    # print(p.contents.x, p.contents.y)
    # changeFunc = clibrary.changePoint
    # changeFunc.argtypes = [ctypes.POINTER(Point)]
    # changeFunc(p)
    # print(p.contents.x, p.contents.y)
    t = ctypes.POINTER(ctypes.c_int)
    print(t)


if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    # p = Process(target=worder)
    p = Process(target=worker)
    # p = Process(target=workstruct)

    p.start()

    p.join()
    print(bin(-1))
    print("Example ffffff")

