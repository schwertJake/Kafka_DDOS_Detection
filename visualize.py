import plotly.offline.offline as py
import plotly.graph_objs as go

def plot(ip_count_list):
    data = [go.Bar(
        x=[x[0] for x in ip_count_list],
        y=[x[1] for x in ip_count_list]
    )]

    py.plot(data, filename='freq.html')

if __name__ == "__main__":
    plot([(1,1), (2,2), (3,3)])