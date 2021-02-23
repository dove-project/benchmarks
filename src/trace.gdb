set breakpoint pending on
# BinaryOp begin
break Enclave/runtime.cpp:327
commands 1
    set record btrace bts buffer-size unlimited
    record btrace
    continue
end

# BinaryOp end
break Enclave/runtime.cpp:378
commands 2
    info record
    record stop
    continue
end

# UnaryOp begin
break Enclave/runtime.cpp:298
commands 3
    set record btrace bts buffer-size unlimited
    record btrace
    continue
end

# UnaryOp end
break Enclave/runtime.cpp:316
commands 4
    info record
    record stop
    continue
end

run
