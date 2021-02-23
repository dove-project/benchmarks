set breakpoint pending on

# Load begin
break main
commands 1
    set record btrace bts buffer-size unlimited
    record btrace
    continue
end

# Load end
break App/App.cpp:92
commands 2
    info record
    record stop
    continue
end

run

