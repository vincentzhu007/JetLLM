'''
模拟分页kvcache的管理过程



模拟Buffer在运行中变长的过程
A[n+1] = B
'''


class BlockMem:
    '''
    每个block块内存
    '''
    block_mem = 4

    def __init__(self):
        self.__mem = [0] * self.block_mem

    def at(self, index):
        return self.__mem[index]

    def set(self, index, value):
        self.__mem[index] = value


class BlockMemMgr:
    '''
    实现一个块内存的管理器，行为：
    - 每次分配的内存最小粒度是block=4
    - 分配的内存不保证连续
    - 总体内存为256，可以分成64块
    '''
    max_block = 64

    '''
    记录逻辑索引和物理索引的关系
    logical_index -> physical_index
    0 -> block 0
    1 -> block 3
    2 -> block 2
    '''
    def __init__(self):
        self.__block_table = {} # key: logical index(int), value: block对象(BlockMem)
        self.length = 0

    '''
    从逻辑内存的角度索引元素
    '''
    def logically_at(self, index):
        if index >= self.length:
            raise IndexError(f'can not find index {index} in block mem')
        block_index = index // BlockMem.block_mem
        block = self.__block_table[block_index]
        return block.at(index % BlockMem.block_mem)

    def logically_set(self, index, value):
        block_index = index // BlockMem.block_mem
        if block_index not in self.__block_table.keys():
            # 触发创建新的block块
            block = BlockMem()
            self.__block_table[block_index] = block

            print(f'[Write triggered block fault], create new block {id(block)} for {index}')
        block = self.__block_table[block_index]
        block.set(index % BlockMem.block_mem, value)
        self.length = max(index + 1, self.length)


    def logically_append(self, value):
        self.logically_set(self.length, value)


    def tostr(self):
        return f'{{len:{self.length}, block_size:{len(self.__block_table)}}}'


class Buffer:
    '''
    模拟Device测的内存
    '''
    def __init__(self):
        self.length = 0
        self.__mem = BlockMemMgr() # Only use in object, not expose to user.

    def set_data(self, alist):
        for i in range(len(alist)):
            self.__mem.logically_set(i, alist[i])
        self.length = len(alist)
        print(f'buffer {id(self)}: set data to {alist}.')

    def append(self, slice):
        '''
        追加内容到Buffer
        '''
        n = slice.length
        for i in range(n):
            self.__mem.logically_append(slice.__mem.logically_at(i))
        self.length += n
        print(f'buffer {id(self)}: append {str(n)} element(s).')

    def at(self, index):
        """
        获取指定索引的内容
        """
        low = -self.length
        high = self.length - 1
        if index < low or index > high :
            raise IndexError(f'Invalid index {str(index)} is out of index range.')
        print(f'buffer {id(self)}: get element at {str(index)}.')
        return self.__mem.logically_at(index)

    def print(self):
        print(f'buffer {id(self)} : [print] length:{self.length}, _mem:{self.__mem.tostr()}')


def test_buffer_append():
    a = Buffer()
    a.set_data([1, 2, 3, 4])
    a.print()

    b = Buffer()
    b.set_data([5, 6, 7])
    b.print()

    print(type(b))
    a.append(b)
    a.print()


def test_buffer_at():
    a = Buffer()
    a.set_data([1, 2, 3, 4])
    a.print()

    for i in range(a.length):
        print(f'a[{i}] = {a.at(i)}')


if __name__ == '__main__':
    test_buffer_append()
    test_buffer_at()
