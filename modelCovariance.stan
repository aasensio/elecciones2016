data {
  int<lower=0> NPartidos;
  int<lower=0> NSondeos;
  int<lower=0> NEmpresas;
  int<lower=0> NDates;
  real<lower=0> sondeos[NSondeos, NPartidos];
  int empresa[NSondeos];
  vector[NSondeos] sigmaSondeo;
  int date[NSondeos];
  vector<lower=0>[NPartidos] alpha;
  matrix[NPartidos,NPartidos] Psi;
}
parameters {
  cov_matrix[NPartidos] Sigma;
  simplex[NPartidos] theta[NDates];
  real house_free[NEmpresas-1,NPartidos];
}

transformed parameters {
  real house[NEmpresas,NPartidos];
  
  for (i in 1:NPartidos) {
    for(k in 1:(NEmpresas-1)) {
      house[k,i] <- house_free[k,i];
    }
    house[NEmpresas,i] <- -sum(house_free[:,i]);
  }
}

model {

  Sigma ~ wishart(NPartidos+2, Psi);

  theta[1] ~dirichlet(alpha);

  for (i in 2:NDates) {
    theta[i] ~ multi_normal(theta[i-1], Sigma);
  }

  for (i in 1:NPartidos) {
    for (j in 1:NEmpresas-1) {
      house_free[j,i] ~ normal(0, 0.05);
    }
  }

  for (i in 1:NSondeos) {
    for (j in 1:NPartidos) {
      if (empresa[i] == 11)        
        sondeos[i,j] ~ normal(theta[date[i],j], sigmaSondeo[i]);
      else
        sondeos[i,j] ~ normal(theta[date[i],j] + house[empresa[i],j], sigmaSondeo[i]);
    }
  }

}