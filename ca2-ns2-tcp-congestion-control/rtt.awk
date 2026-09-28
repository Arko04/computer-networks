BEGIN {
    count = 0;
    sum_rtt = 0;
}

{
    event = $1;
    time = $2;
    from_node = $3;
    to_node = $4;
    pkt_type = $5;
    seq_num = $11;

    if (event == "+" && from_node == fsrc && pkt_type == "tcp") {
        send_time[seq_num] = time;
    }

    if (event == "r" && to_node == fsrc && pkt_type == "ack") {
        if (seq_num in send_time) {
            rtt = time - send_time[seq_num];
            sum_rtt += rtt;
            count++;
            delete send_time[seq_num];
        }
    }
}

END {
    if (count > 0) {
        printf "%.4f", (sum_rtt / count) * 1000;
    } else {
        print "0";
    }
}