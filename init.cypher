// Ensure username is unique
CREATE CONSTRAINT unique_username FOR (a:Account) REQUIRE a.username IS UNIQUE;

// Create indexes for performance optimization
CREATE INDEX account_follows_idx FOR (a:Account) ON (a.follows_count);
CREATE INDEX account_followers_idx FOR (a:Account) ON (a.followers_count);
CREATE INDEX account_username_idx FOR (a:Account) ON (a.username);