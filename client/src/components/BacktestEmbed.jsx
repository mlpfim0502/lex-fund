function BacktestEmbed() {
    return (
        <div style={{
            height: 'calc(100vh - 70px)',
            width: '100%',
            overflow: 'hidden'
        }}>
            <iframe
                src="http://localhost:5001?embed=true"
                style={{
                    width: '100%',
                    height: '100%',
                    border: 'none'
                }}
                title="Strategy Backtest"
            />
        </div>
    );
}

export default BacktestEmbed;
