using namespace std;
#include <bits/stdc++.h>
#define ll long long
#define FOR(i,n) for(int (i)=0;(i)<(n);++(i))
#define PRE(i, m, n, in) for(int (i)=(m);(i)<(n);i+=in)
#define srt(v) sort(v.begin(),v.end())
#define printv(a) printa(a,0,a.size())
#define debug(x) cout<<#x" = "<<(x)<<endl
#define printa(a,L,R) for(int i=L;i<R;i++) cout<<a[i]<<(i==R-1?"\n":" ")
#define printv(a) printa(a,0,a.size())
#define print2d(a,r,c) for(int i=0;i<r;i++) for(int j=0;j<c;j++) cout<<a[i][j]<<(j==c-1?"\n":" ")
typedef vector<string>VS;
typedef pair<ll,ll>II;
typedef vector<ll>VL;
typedef vector<int>VI;
typedef vector<VI>VVI;
typedef vector<VL>VVL;
typedef vector<II>VII;

int main() {
  ios_base::sync_with_stdio(false);
  cin.tie(NULL);
  int n; cin >> n;
  vector<double>p(n);
  FOR(i,n) cin >> p[i];
  vector<vector<double>>dp(n+1,vector<double>(n+1));
  dp[0][0]=1;
  PRE(i, 1, n+1, 1) {
    dp[i][0] = dp[i-1][0]*p[i-1];
    dp[0][i] = dp[0][i-1]*(1-p[i-1]);
  }
  double res=0;
  PRE(i,1,n+1,1) {
    PRE(j,1,n+1-i,1){
      dp[i][j] = dp[i-1][j]*p[i] + dp[i][j-1]*(1-p[i]);
    } 
  }
cout<<res<<endl;
  PRE(i,n/2+1,n+1,1) {
    res += dp[i][n-i];
    debug(dp[i][n-i]);
  }
  print2d(dp,n+1,n+1);
  cout<<res<<endl;
  //cout<<fixed<<setprecision(6) << res<<endl;
  cout<<res<<endl;
  return 0;
}
